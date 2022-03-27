import asyncio
import logging
import grpc
import post_pb2_grpc
import post_pb2

async def delete_post(stub:post_pb2_grpc.postServiceServicer):
    success = False
    try:
        success = await stub.deletePost(post_pb2.uid(id='623fe0ccee69055e4871bf26'))
    except Exception as e:
        print(f"[ERROR]: {e}")
    finally:

        print("-------DELETE POST---------")
        if success:
            print("deleted post successfully")
        else:
            print("Couldnt delete post successfully")
        print("-------DELETE POST---------")

async def read_post(stub:post_pb2_grpc.postServiceServicer):
    post = None
    try:
        post = await stub.readOne(post_pb2.uid(id='623f53aae6c7006cb6a4e8f6'))
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

async def update_post(stub:post_pb2_grpc.postServiceServicer):
    post = None
    try:
        data = post_pb2.aPost(
                id = "623f53aae6c7006cb6a4e8f6",
                title = "cricket",
                body = "my fav is AR",
                author = "chandra69@",
                creationDate = "26-03-22",
                lastUpdatedDate = "31-03-22",
                )

        post = await stub.updatePost(data)
        print("post:",post)
    except Exception as e:
        print(f"[ERROR]: {e}")
    finally:
        if not (post.body and post.title and post.author):
            print("Server returned empty post!!")
            return

        print("-------UPDATED POST---------")
        print("title:",post.title)
        print("author:",post.author)
        print("body:",post.body)
        print("----------UPDATED POST-------")

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

        # print("-------CREATE POST-------")
        # await create_post(stub)

        # print("-------------READ POST-------------")
        # await read_post(stub)

        # print("-------Update Post-------")
        # await update_post(stub)

        print("-------DELETE POST---------")
        await delete_post(stub)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.get_event_loop().run_until_complete(main())