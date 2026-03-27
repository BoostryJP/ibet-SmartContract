import brownie
import pytest
from Crypto.Hash import SHA256
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS


class _RawHash:
    block_size = 64
    digest_size = 32
    oid = SHA256.new(b"").oid

    def __init__(self, data: bytes):
        self._data = data

    @classmethod
    def new(cls, data=b""):
        return cls(data)

    def update(self, data: bytes):
        self._data += data

    def copy(self):
        return self.__class__(self._data)

    def digest(self):
        return self._data


def _generate_p256_signature(private_key, tx_hash):
    signer = DSS.new(private_key, "deterministic-rfc6979", encoding="binary")
    if isinstance(tx_hash, (bytes, bytearray)):
        tx_hash_bytes = bytes(tx_hash)
    else:
        tx_hash_hex = tx_hash.hex() if hasattr(tx_hash, "hex") else str(tx_hash)
        if tx_hash_hex.startswith("0x"):
            tx_hash_hex = tx_hash_hex[2:]
        tx_hash_bytes = bytes.fromhex(tx_hash_hex)

    signature = signer.sign(_RawHash(tx_hash_bytes))

    return (
        int.from_bytes(signature[:32], byteorder="big"),
        int.from_bytes(signature[32:], byteorder="big"),
    )


def _generate_p256_keypair():
    private_key = ECC.generate(curve="P-256")
    return private_key, int(private_key.pointQ.x), int(private_key.pointQ.y)


# TEST_deploy
class TestDeploy:
    # Normal_1
    def test_normal_1(self, P256Wallet, users):
        admin = users["admin"]
        pubkey_x = 1
        pubkey_y = 2

        wallet = admin.deploy(P256Wallet, pubkey_x, pubkey_y)

        assert wallet.pubKeyX() == pubkey_x
        assert wallet.pubKeyY() == pubkey_y
        assert wallet.nonce() == 0

    # Error_1
    def test_error_1(self, P256Wallet, users):
        admin = users["admin"]

        with pytest.raises(ValueError):
            admin.deploy(P256Wallet, 0, 2)

        with pytest.raises(ValueError):
            admin.deploy(P256Wallet, 2, 0)


# TEST_getTransactionHash
class TestGetTransactionHash:
    # Normal_1
    def test_normal_1(self, P256Wallet, users):
        admin = users["admin"]
        wallet = admin.deploy(P256Wallet, 10, 20)

        target = users["user1"].address
        value = 123
        data = "0x11223344"
        nonce = 7

        tx_hash = wallet.getTransactionHash.call(target, value, data, nonce)

        assert tx_hash != "0x" + "00" * 32


# TEST_execute
class TestExecute:
    # Normal_1
    # valid signature should succeed
    def test_normal_1(self, P256Wallet, WalletTestReceiver, users):
        admin = users["admin"]
        receiver = admin.deploy(WalletTestReceiver)
        value_to_set = 12345
        call_data = receiver.setValue.encode_input(value_to_set)

        private_key, pubkey_x, pubkey_y = _generate_p256_keypair()
        wallet = admin.deploy(P256Wallet, pubkey_x, pubkey_y)
        tx_hash = wallet.getTransactionHash.call(receiver.address, 0, call_data, 0)
        sig_r, sig_s = _generate_p256_signature(private_key, tx_hash)

        tx = wallet.execute(
            receiver.address,
            0,
            call_data,
            sig_r,
            sig_s,
            {"from": users["user1"]},
        )

        assert receiver.lastValue() == value_to_set
        assert receiver.lastCaller() == wallet.address
        assert wallet.nonce() == 1

        assert tx.events["Executed"]["target"] == receiver.address
        assert tx.events["Executed"]["value"] == 0
        assert tx.events["Executed"]["data"] == call_data
        assert tx.events["Executed"]["nonce"] == 0

    # Error_1
    # invalid signature should always fail
    def test_error_1(self, P256Wallet, WalletTestReceiver, users):
        admin = users["admin"]
        wallet = admin.deploy(P256Wallet, 1, 2)
        receiver = admin.deploy(WalletTestReceiver)

        call_data = receiver.setValue.encode_input(999)

        with brownie.reverts(revert_msg="630101"):
            wallet.execute(
                receiver.address,
                0,
                call_data,
                0,
                0,
                {"from": users["user1"]},
            )
