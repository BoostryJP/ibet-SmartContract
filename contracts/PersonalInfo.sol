pragma solidity ^0.4.19;

contract PersonalInfo {

    // 暗号化個人情報
    struct Info {
        address account_address; // アカウントアドレス
        address issuer_address; // アカウントアドレス（発行体）
        string encrypted_info; // 氏名・住所（暗号化済）
    }

    // 名簿記載用個人情報
    // acount_address => issuer_address => info
    mapping(address => mapping(address => Info)) public personal_info;

    // イベント：登録
    event Register(address indexed account_address, address indexed issuer_address);

    // コンストラクタ
    function PersonalInfo() public {
    }

    // ファンクション：情報を登録する
    function register(address _issuer_address, string _encrypted_info) public returns (bool) {
        Info storage info = personal_info[msg.sender][_issuer_address];

        info.account_address = msg.sender;
        info.issuer_address = _issuer_address;
        info.encrypted_info = _encrypted_info;

        emit Register(msg.sender, _issuer_address);

        return true;
    }

    // ファンクション：登録状況を確認する
    function isRegistered(address _account_address, address _issuer_address) public view returns (bool) {
        Info storage info = personal_info[_account_address][_issuer_address];
        if (info.account_address == 0) {
            return false;
        } else {
            return true;
        }
    }

}
