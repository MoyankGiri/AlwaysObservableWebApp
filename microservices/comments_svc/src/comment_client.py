from sre_constants import SUCCESS
import comments_pb2
import comments_pb2_grpc
import asyncio
import logging
import grpc

async def read_comment(stub:comments_pb2_grpc.commentServiceServicer):
    comment = None
    try:
        comment = await stub.readComments(comments_pb2.uid(id='623f53aae6c7006cb6a4e8f6'))
    except Exception as e:
        print(f"[ERROR]: {e}")
    finally:
        if not (comment.id and comment.body and comment.author and comment.parentPost and comment.parentComment):
            print("Nothing was found...")
            return 
        print("--------- READ COMMENT ---------")
        print("ID ",comment.id)
        print("Body ",comment.body )
        print("Author ",comment.author )
        print("ParentPost ",comment.parentPost )
        print("parentComment ",comment.parentComment)
        print("--------- READ COMMENT ---------")

async def create_comment(stub:comments_pb2_grpc.commentServiceServicer):
    newComment = None
    try:
        newComment = await stub.createComment(comments_pb2.aComment(title = input(),body = input(),author = input(),parentPost = input(),parentComment = input(),userID = input()))
    except Exception as e:
        print(f"[ERROR]: {e}")
    finally:
        if not (newComment.title and newComment.body and newComment.author):
            print("ERROR")
            return 
        print("--------- CREATE COMMENT ---------")
        print("ID ",newComment.id)
        print("User ID",newComment.userID)
        print("Body ",newComment.body )
        print("Author ",newComment.author )
        print("ParentPost ",newComment.parentPost )
        print("parentComment ",newComment.parentComment)
        print("--------- CREATE COMMENT ---------")


async def main():
    async with grpc.aio.insecure_channel('localhost:50051') as channel:
        stub = comments_pb2_grpc.commentServiceStub(channel)

        await create_comment(stub)

        #await read_comment(stub)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.get_event_loop().run_until_complete(main())