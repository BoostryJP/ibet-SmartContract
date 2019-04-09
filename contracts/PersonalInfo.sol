pragma solidity ^0.4.24;

contract PersonalInfo {

    // 暗号化個人情報
    struct Info {
        address account_address; // アカウントアドレス
        address link_address; // 情報を公開する先のアドレス
        string encrypted_info; // 暗号化済個人情報
    }

    // 名簿記載用個人情報
    // acount_address => link_address => info
    mapping(address => mapping(address => Info)) public personal_info;

    // イベント：登録
    event Register(address indexed account_address, address indexed link_address);

    // コンストラクタ
    constructor() public {
    }

    // ファンクション：情報を登録する
    function register(address _link_address, string memory _encrypted_info) public returns (bool) {
        Info storage info = personal_info[msg.sender][_link_address];

        info.account_address = msg.sender;
        info.link_address = _link_address;
        info.encrypted_info = _encrypted_info;

        emit Register(msg.sender, _link_address);

        return true;
    }

    // ファンクション：登録状況を確認する
    function isRegistered(address _account_address, address _link_address) public view returns (bool) {
        Info storage info = personal_info[_account_address][_link_address];
        if (info.account_address == 0x0000000000000000000000000000000000000000) {
            return false;
        } else {
            return true;
        }
    }

}
