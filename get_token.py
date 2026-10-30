import yadisk

client = yadisk.Client(
    id="88468c9cea12421389bc51d435fc71e1",
    secret="416fbe76eb1a4684a8cf6a0f06dd12b4"
)
print(client.get_auth_url("token"))