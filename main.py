import asyncio
import grpc
import numpy as np
from concurrent import futures
import proto.story_pb2 as story_pb2
import proto.story_pb2_grpc as story_pb2_grpc
from trendfetching import get_pakistan_trending_searches 

class StoryService(story_pb2_grpc.StoryServiceServicer):
    def __init__(self, region):
        # Load the dataframe once when the server starts
        self.df = get_pakistan_trending_searches(region)
        self.region = region

    async def GenerateStory(self, request, context):
        # Generate the story and fetch trends within the generate_story method
        story_text, trending_searches = await self.generate_story(request.topic, request.theme)
        return story_pb2.StoryResponse(
            story=story_text,
            region=self.region,
            trends=" ".join(trending_searches),
            status="success"
        )

    async def generate_story(self, topic, theme):
        # Use the preloaded dataframe
        numbers = np.arange(len(self.df['search_term']))
        trending_searches = self.df['search_term'].tolist()
        trend_dict = dict(zip(numbers, trending_searches))
        
        await asyncio.sleep(1)  # simulate async I/O
        story_text = f"A {theme} story about {topic} from {self.region}. List of trends is {trend_dict}."
        return story_text, trending_searches


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
