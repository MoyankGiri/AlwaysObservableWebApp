import asyncio
import logging
from multiprocessing import AuthenticationError
import grpc
import post_pb2_grpc
import post_pb2

async def read_post(stub:post_pb2_grpc.postServiceServicer):
    post = None
    try:
        post = await stub.readOne(post_pb2.uid(id='2'))
        print("post:",post)
    except Exception as e:
        print(f"[ERROR]: {e}")
    finally:
        if not (post.body and post.title and post.author):
            print("Server returned empty post!!")
            return

        print("-------POST---------")
        print("title:",post.title)
        print("author:",post.author)
        print("body:",post.body)
        print("----------POST-------")

async def create_post(stub:post_pb2_grpc.postServiceServicer):
    post = None
    try:
        post = await stub.create(post_pb2.newPost(title=input(),body=input(),author=input()))
        print("new post:",post)
    except Exception as e:
        print("[ERROR]:",e)
    finally:
        if not (post.body and post.title and post.author):
            print("Server returned empty post!!")
            return

        print("-------POST CREATED---------")
        print("title:",post.title)
        print("author:",post.author)
        print("body:",post.body)
        print("----------POST CREATED-------")


async def main():
    async with grpc.aio.insecure_channel('localhost:50051') as channel:
        stub = post_pb2_grpc.postServiceStub(channel)

        print("-------CREATE POST-------")
        await create_post(stub)

        print("-------------READ POST-------------")
        await read_post(stub)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.get_event_loop().run_until_complete(main())