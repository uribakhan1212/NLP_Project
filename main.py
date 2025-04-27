import asyncio
import grpc
from concurrent import futures
import proto.story_pb2 as story_pb2
import proto.story_pb2_grpc as story_pb2_grpc

class StoryService(story_pb2_grpc.StoryServiceServicer):
    async def GenerateStory(self, request, context):
        # Fake async story generation
        story_text = await self.generate_story(request.topic, request.theme)
        return story_pb2.StoryResponse(
            story=story_text,
            status="success"
        )

    async def generate_story(self, topic, theme):
        await asyncio.sleep(1)  # simulate async I/O
        return f"A {theme} story about {topic}."

async def serve():
    server = grpc.aio.server()
    story_pb2_grpc.add_StoryServiceServicer_to_server(StoryService(), server)
    server.add_insecure_port('[::]:50051')
    await server.start()
    print("gRPC server running on port 50051 🚀")
    await server.wait_for_termination()

if __name__ == "__main__":
    asyncio.run(serve())
