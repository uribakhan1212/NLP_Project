import asyncio
import grpc
import numpy as np
from concurrent import futures
import proto.story_pb2 as story_pb2
import proto.story_pb2_grpc as story_pb2_grpc
from trendfetching import get_pakistan_trending_searches
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True
)

tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.2")
model = AutoModelForCausalLM.from_pretrained(
    "mistralai/Mistral-7B-Instruct-v0.2",
    quantization_config=bnb_config,
    device_map={"": "cuda:0"}
)

def get_prompt(topic, theme):
    return f"""
    [System]
    You are an expert storyteller and creative writer. You always produce complete, well-structured narratives, with vivid descriptions, coherent plots, and satisfying endings. You never truncate your sentences or stop abruptly; if more text is needed, continue until the story is complete.

    [User]
    Write a single short story of about 800-1,000 words on the topic of {topic} The story should:
    • Introduce memorable characters  
    • Establish the setting and conflict clearly  
    • Develop rising action, climax, and resolution  
    • Use rich sensory details and dialogue  
    • Conclude with a thoughtful reflection or twist  

    Give the story a title that captures its essence. The story should be engaging and thought-provoking, leaving the reader with a sense of closure and satisfaction. Use a formal tone and avoid slang or colloquial expressions. The story should be suitable for a general audience and not contain any explicit content or offensive language.
    The theme of the story is {theme}.
    [Assistant]
    """

class StoryService(story_pb2_grpc.StoryServiceServicer):
    def __init__(self, region):
        # Load the dataframe once when the server starts
        #self.df = get_pakistan_trending_searches(region)
        #self.region = region
        self.request_queue = asyncio.Queue()  # Queue to manage incoming requests
        self.processing_task = asyncio.create_task(self._process_requests())  # Background task to process requests

    async def GetTrends(self, request, context):
        """Fetch trends based on the selected region."""
        try:
            # Generate trends for the requested region
            self.df = get_pakistan_trending_searches(request.region)
            self.region = request.region
            print("Region fetched from input is: ", self.region)
            trends = self.generate_trends()
            return story_pb2.TrendsResponse(
                trends=trends,
                status="success"
            )
        except Exception as e:
            return story_pb2.TrendsResponse(
                trends=[],
                status=f"error: {str(e)}"
            )

    async def GenerateStory(self, request, context):
        """Generate a story based on the selected trend and theme."""
        # Add the request to the queue and wait for the result
        response_future = asyncio.Future()
        self.selected_trend = request.topic
        await self.request_queue.put((request, response_future))
        try:
            response = await response_future
            return response
        except Exception as e:
            # Handle errors and communicate them back to the client
            return story_pb2.StoryResponse(
                story="",
                region=self.region,
                trends="",
                status=f"error: {str(e)}"
            )

    async def _process_requests(self):
        while True:
            request, response_future = await self.request_queue.get()
            try:
                # Process the request
                trending_searches = self.generate_trends()
                print(self.selected_trend)
                story_text = await self.generate_story(self.selected_trend, request.theme, trending_searches)
                response = story_pb2.StoryResponse(
                    story=story_text,
                    region=self.region,
                    trends=" ".join(trending_searches),
                    status="success"
                )
                response_future.set_result(response)
            except Exception as e:
                response_future.set_exception(e)
            finally:
                self.request_queue.task_done()

    def generate_trends(self):
        """Use the preloaded dataframe to generate trends."""
        return self.df['search_term'].tolist()

    async def generate_story(self, topic, theme, trending_searches):
        """Simulate generating a story."""
        await asyncio.sleep(1)  # Simulate async I/O
        #story_text = f"A {theme} story about {topic} from {self.region}. List of trends is {trending_searches}."

        inputs = tokenizer(get_prompt(topic, theme), return_tensors="pt").to("cuda:0")
        outputs = model.generate(
            **inputs,
            max_new_tokens=1024,
            temperature=0.8,
            top_p=0.9,
            repetition_penalty=1.1,
            do_sample=True,
            num_return_sequences=1,
            eos_token_id=tokenizer.eos_token_id,
            pad_token_id=tokenizer.eos_token_id,
        )

        generated = outputs[0][ inputs["input_ids"].size(-1) : ].tolist()
        story = tokenizer.decode(generated, skip_special_tokens=True)
        print(story)
        return story


async def serve():
    region = "PK"  # Set the region here
    server = grpc.aio.server()
    story_service = StoryService(region)
    story_pb2_grpc.add_StoryServiceServicer_to_server(story_service, server)
    server.add_insecure_port('[::]:50051')
    await server.start()
    print("gRPC server running on port 50051 🚀")
    await server.wait_for_termination()

if __name__ == "__main__":
    asyncio.run(serve())