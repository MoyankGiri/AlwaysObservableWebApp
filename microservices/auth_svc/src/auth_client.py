import asyncio
import logging
import grpc
import user_pb2_grpc
import user_pb2

async def createAccount(stub:user_pb2_grpc.userServiceServicer):
    success = None
    try:
        success = await stub.createAccount(user_pb2.aUser(username="dhoni",password="secret"))
        print(success)
    except Exception as e:
        print(f"[ERROR]: {e}")
    finally:
        print(f"Success {success}")

async def login(stub:user_pb2_grpc.userServiceServicer):
    success = None
    try:
        success = await stub.login(user_pb2.aUser(username="dhoni",password="secret"))
        print(success)
        return success
    except Exception as e:
        print(f'[ERROR]: {e}')
    finally:
        print(f"success {success}")

async def auth(stub:user_pb2_grpc.userServiceServicer,token):
    succeess = None
    try:
        succeess = await stub.auth(user_pb2.header(token=token))
        print(succeess)
    except Exception as e:
        print(f'[ERROR] : {e}')
        
async def main():
    async with grpc.aio.insecure_channel('localhost:50051') as channel:
        stub = user_pb2_grpc.userServiceStub(channel)

        # print("-------CREATE ACCOUNT-------")
        # await createAccount(stub)

        print("------LOGIN--------")
        success = await login(stub)

        print("-------AUTH----------")
        await auth(stub,success.token)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.get_event_loop().run_until_complete(main())