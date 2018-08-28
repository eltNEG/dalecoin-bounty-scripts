pragma solidity 0.4.24;

contract Token {
    
    uint8 public decimals;

    function totalSupply() constant returns (uint256 supply) {}

    function balanceOf(address _owner) constant returns (uint256 balance) {}

    function transfer(address _to, uint256 _value) public returns (bool success) {}
    
    function transferFrom(address _from, address _to, uint256 _value) public returns (bool success) {}

    event Transfer(address indexed _from, address indexed _to, uint256 _value);

    event Approval(address indexed _owner, address indexed _spender, uint256 _value);

}

contract Distributor {
    address public owner;
    Token public currentToken;
    uint public tokenDecimal;

    constructor() public {
        owner = msg.sender;
        currentToken = Token(0x07d9e49ea402194bf48a8276dafb16e4ed633317);
        tokenDecimal = currentToken.decimals();
    }

    modifier onlyOwner() {
      require(msg.sender == owner);
      _;
    }

    function withdrawToken(Token tokenAddress, address _to, uint _value) public onlyOwner returns (bool success) {
        tokenAddress.transfer(_to, _value);
        return true;
    }

    function withdrawEther() public onlyOwner returns(bool success){
        address dalcDistrContractAddr = this;
        owner.transfer(dalcDistrContractAddr.balance);
        return true;
    }

    //multiply value to be distributed by 1000
    function distributeToken (address[] addresses, uint256[] value ) public onlyOwner returns(uint number) {
        for ( uint256 i = 0; i < addresses.length; i++) {
            currentToken.transfer(addresses[i], (value[i] * 10**(tokenDecimal-3)) );
        }
        return i;
    }
    
    function airdropToken (address[] addresses, uint256 value ) public onlyOwner returns(uint number) {
        for ( uint256 i = 0; i < addresses.length; i++) {
            currentToken.transfer(addresses[i], value * 10 ** tokenDecimal);
        }
        return i;
    }

    function setToken (address newToken) public onlyOwner {
        currentToken = Token(newToken);
        tokenDecimal = currentToken.decimals();
    }

    function tokenBalance(Token tokenAddress) public view returns(uint value) {
        address dalcDistrContractAddr = this;
        return tokenAddress.balanceOf(dalcDistrContractAddr);
    }

    function destroy (address _to) public {
        require(msg.sender == owner);
        selfdestruct(_to);
    }
}