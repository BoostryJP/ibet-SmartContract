## Error Code
This is a definition list of errors to be thrown when transaction reverts.
Developers will receive error msg as code, and each error code is described below, including description of situation and possible causes.

### Token Error
- [TokenList (10XXXX)](#tokenlist-10XXXX)
- [IbetShare (11XXXX)](#ibetshare-11XXXX)
- [IbetStraightBond (12XXXX)](#ibetstraightbond-12XXXX)
- [IbetCoupon (13XXXX)](#ibetcoupon-13XXXX)
- [IbetMembership (14XXXX)](#ibetmembership-14XXXX)
- [IbetStandardToken (15XXXX)](#ibetstandardtoken-15XXXX)

### Exchange & Escrow Error
- [ExchangeStorage (20XXXX)](#exchangestorage-20XXXX)
- [IbetExchange (21XXXX)](#ibetexchange-21XXXX)
- [EscrowStorage (22XXXX)](#escrowstorage-22XXXX)
- [IbetEscrow (23XXXX)](#ibetescrow-23XXXX)
- [IbetSecurityTokenEscrow (24XXXX)](#ibetsecuritytokenescrow-24XXXX)

### Payment Error
- [PaymentGateway (30XXXX)](#paymentgateway-30XXXX)

### Ledger Error
- [PersonalInfo (40XXXX)](#personalinfo-40XXXX)

### Access Error
- [Ownable (50XXXX)](#ownable-50XXXX)

### Utils Error
- [ContractRegistry (60XXXX)](#contractregistry-60XXXX)
- [E2EMessaging (61XXXX)](#e2emessaging-61XXXX)
- [FreezeLog (62XXXX)](#freezelog-62XXXX)

### TokenList (10XXXX)

#### register (1000XX)

| Code       | Situation                                | Possible causes | 
|------------|------------------------------------------|-----------------|
| **100001** | The address has already been registered. | -               |
| **100002** | Message sender must be the token owner.  | -               |

#### changeOwner (1001XX)

| Code       | Situation                               | Possible causes | 
|------------|-----------------------------------------|-----------------|
| **100101** | The address has not been registered.    | -               |
| **100102** | Message sender must be the token owner. | -               |

### IbetShare (11XXXX)

#### lock (1100XX)

| Code       | Situation                                           | Possible causes                                                                                                                      | 
|------------|-----------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------|
| **110001** | Lock address is invalid.                            | Any of following conditions is not matched.<br/> - Lock address isn't authorized for locking.<br/> - Lock Address isn't token owner. |
| **110002** | Lock amount is greater than message sender balance. | -                                                                                                                                    |

#### unlock (1101XX)

| Code       | Situation                                    | Possible causes                                                                                                                          | 
|------------|----------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------|
| **110101** | Unlock address is invalid.                   | Any of following conditions is not matched.<br/> - Unlock address isn't authorized for locking.<br/> - Unlock Address isn't token owner. |
| **110102** | Unlock amount is greater than locked amount. | -                                                                                                                                        |

#### transferToAddress (1102XX)

| Code       | Situation                            | Possible causes                                                                                                                                                        | 
|------------|--------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **110201** | The token isn't transferable.        | All of following conditions is matched.<br/> - Message sender isn't tradable Exchange.<br/> - Approval is required for the token transferring.                         |
| **110202** | Destination address check is failed. | All of following conditions is matched.<br/> - Destination address isn't token owner.<br/> - Destination address isn't registered personal information to token owner. |

#### transferToContract (1103XX)

| Code       | Situation                                    | Possible causes | 
|------------|----------------------------------------------|-----------------|
| **110301** | Destination address isn't tradable exchange. | -               |

#### transfer (1104XX)

| Code       | Situation                               | Possible causes | 
|------------|-----------------------------------------|-----------------|
| **110401** | Message sender balance is insufficient. | -               |
| **110402** | The token isn't transferable.           | -               |

#### bulkTransfer (1105XX)

| Code       | Situation                                             | Possible causes                                                                                                                                | 
|------------|-------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------|
| **110501** | Transferring of this token requires approval.         | -                                                                                                                                              |
| **110502** | Length of To and of Value aren't matched.             | -                                                                                                                                              |
| **110503** | Transfer amount is greater than from address balance. | -                                                                                                                                              |
| **110504** | The token isn't transferable.                         | All of following conditions is matched.<br/> - Message sender isn't tradable Exchange.<br/> - Approval is required for the token transferring. |

#### transferFrom (1106XX)

| Code       | Situation                                             | Possible causes | 
|------------|-------------------------------------------------------|-----------------|
| **110601** | Transfer amount is greater than from address balance. | -               |

#### applyForTransfer (1107XX)

| Code       | Situation                            | Possible causes                                                                                                                                                                          | 
|------------|--------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **110701** | Apply for transfer is invalid.       | Any of following conditions is matched.<br/> - Approval is not required for the token transferring.<br/> - The token is not transferable.<br/> - Message sender balance is insufficient. |
| **110702** | Destination address check is failed. | All of following conditions is matched.<br/> - Destination address isn't token owner.<br/> - Destination address hasn't registered personal information to token owner.                  |

#### cancelTransfer (1108XX)

| Code       | Situation                                      | Possible causes                                                                                                                 | 
|------------|------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------|
| **110801** | Canceling application for transfer is invalid. | All of following conditions is matched.<br/> - Message sender isn't application owner.<br/> - Message sender isn't token owner. |
| **110802** | Application is invalid.                        | -                                                                                                                               |

#### approveTransfer (1109XX)

| Code       | Situation                 | Possible causes | 
|------------|---------------------------|-----------------|
| **110901** | Token isn't transferable. | -               |
| **110902** | Application is invalid.   | -               |

#### applyForOffering (1110XX)

| Code       | Situation                                                               | Possible causes | 
|------------|-------------------------------------------------------------------------|-----------------|
| **111001** | Offering is stopped.                                                    | -               |
| **111002** | Personal information of message sender isn't registered to token owner. |                 |

#### redeemFrom (1111XX)

| Code       | Situation                                          | Possible causes | 
|------------|----------------------------------------------------|-----------------|
| **111101** | Redeem amount is less than locked address balance. | -               |
| **111102** | Redeem amount is less than target address balance. | -               |

#### forceUnlock (1112XX)

| Code       | Situation                                          | Possible causes | 
|------------|----------------------------------------------------|-----------------|
| **111201** | Unlock amount is greater than locked amount.       | -               |

#### bulkIssueFrom (1113XX)

| Code       | Situation                                                                      | Possible causes | 
|------------|--------------------------------------------------------------------------------|-----------------|
| **111301** | The length of the target address, the lock address and the amount don't match. | -               |

#### bulkRedeemFrom (1114XX)

| Code       | Situation                                                                      | Possible causes | 
|------------|--------------------------------------------------------------------------------|-----------------|
| **111401** | The length of the target address, the lock address and the amount don't match. | -               |

#### bulkTransferFrom (1115XX)

| Code       | Situation                                   | Possible causes | 
|------------|---------------------------------------------|-----------------|
| **111501** | The From, To and Value lengths don't match. | -               |

#### forceLock (1116XX)
| Code       | Situation                                           | Possible causes | 
|------------|-----------------------------------------------------|-----------------|
| **111601** | Lock amount is greater than message sender balance. | -               |

### IbetStraightBond (12XXXX)

#### lock (1200XX)

| Code       | Situation                                           | Possible causes                                                                                                                      | 
|------------|-----------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------|
| **120001** | Lock address is invalid.                            | Any of following conditions is not matched.<br/> - Lock address isn't authorized for locking <br/> - Lock Address isn't token owner. |
| **120002** | Lock amount is greater than message sender balance. | -                                                                                                                                    |

#### unlock (1201XX)

| Code       | Situation                                    | Possible causes                                                                                                                          | 
|------------|----------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------|
| **120101** | Unlock address is invalid.                   | Any of following conditions is not matched.<br/> - Unlock address isn't authorized for locking <br/> - Unlock Address isn't token owner. |
| **120102** | Unlock amount is greater than locked amount. | -                                                                                                                                        |

#### transferToAddress (1202XX)

| Code       | Situation                            | Possible causes                                                                                                                                                         | 
|------------|--------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **120201** | The token isn't transferable.        | All of following conditions is matched.<br/> - Message sender isn't tradable Exchange.<br/> - Approval is required for the token transferring.                          |
| **120202** | Destination address check is failed. | All of following conditions is matched.<br/> - Destination address isn't token owner.<br/> - Destination address hasn't registered personal information to token owner. |

#### transferToContract (1203XX)

| Code       | Situation                                    | Possible causes | 
|------------|----------------------------------------------|-----------------|
| **120301** | Destination address isn't tradable exchange. | -               |

#### transfer (1204XX)

| Code       | Situation                               | Possible causes | 
|------------|-----------------------------------------|-----------------|
| **120401** | Message sender balance is insufficient. | -               |
| **120402** | The token isn't transferable.           | -               |

#### bulkTransfer (1205XX)

| Code       | Situation                                             | Possible causes                                                                                                             | 
|------------|-------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------|
| **120501** | Length of To and of Value aren't matched.             | -                                                                                                                           |
| **120502** | Transfer amount is greater than from address balance. | -                                                                                                                           |
| **120503** | The token isn't transferable.                         | All of following conditions is matched.<br/> - Message sender isn't tradable Exchange.<br/> - The token isn't transferable. |

#### transferFrom (1206XX)

| Code       | Situation                                             | Possible causes | 
|------------|-------------------------------------------------------|-----------------|
| **120601** | Transfer amount is greater than from address balance. | -               |

#### applyForTransfer (1207XX)

| Code       | Situation                            | Possible causes                                                                                                                                                                                           | 
|------------|--------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **120701** | Apply for transfer is invalid.       | Any of following conditions is matched.<br/> - Approval is not required for the token transferring.<br/> - The token is not transferable.<br/> - Message sender balance is less than transferring amount. |
| **120702** | Destination address check is failed. | All of following conditions is matched.<br/> - Destination address isn't token owner.<br/> - Destination address hasn't registered personal information to token owner.                                   || **a**    |                                        |                                                                                                                                                                                                          |

#### cancelTransfer (1208XX)

| Code       | Situation                                      | Possible causes                                                                                                                 | 
|------------|------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------|
| **120801** | Canceling application for transfer is invalid. | All of following conditions is matched.<br/> - Message sender isn't application owner.<br/> - Message sender isn't token owner. |
| **120802** | Application is invalid.                        | -                                                                                                                               |

#### approveTransfer (1209XX)

| Code       | Situation                 | Possible causes | 
|------------|---------------------------|-----------------|
| **120901** | Token isn't transferable. | -               |
| **120902** | Application is invalid.   | -               |

#### applyForOffering (1210XX)

| Code       | Situation                                                               | Possible causes | 
|------------|-------------------------------------------------------------------------|-----------------|
| **121001** | Offering is stopped.                                                    | -               |
| **121002** | Personal information of message sender isn't registered to token owner. |                 |

#### redeemFrom (1211XX)

| Code       | Situation                                          | Possible causes | 
|------------|----------------------------------------------------|-----------------|
| **121101** | Redeem amount is less than locked address balance. | -               |
| **121102** | Redeem amount is less than target address balance. | -               |

#### forceUnlock (1212XX)

| Code       | Situation                                          | Possible causes | 
|------------|----------------------------------------------------|-----------------|
| **121201** | Unlock amount is greater than locked amount.       | -               |

#### bulkIssueFrom (1213XX)

| Code       | Situation                                                                      | Possible causes | 
|------------|--------------------------------------------------------------------------------|-----------------|
| **121301** | The length of the target address, the lock address and the amount don't match. | -               |

#### bulkRedeemFrom (1214XX)

| Code       | Situation                                                                      | Possible causes | 
|------------|--------------------------------------------------------------------------------|-----------------|
| **121401** | The length of the target address, the lock address and the amount don't match. | -               |

#### bulkTransferFrom (1215XX)

| Code       | Situation                                   | Possible causes | 
|------------|---------------------------------------------|-----------------|
| **121501** | The From, To and Value lengths don't match. | -               |

#### forceLock (1216XX)
| Code       | Situation                                           | Possible causes | 
|------------|-----------------------------------------------------|-----------------|
| **121601** | Lock amount is greater than message sender balance. | -               |

### IbetCoupon (13XXXX)

#### transferToContract (1300XX)

| Code       | Situation                                    | Possible causes | 
|------------|----------------------------------------------|-----------------|
| **130001** | Destination address isn't tradable exchange. | -               |

#### transfer (1301XX)

| Code       | Situation                               | Possible causes | 
|------------|-----------------------------------------|-----------------|
| **130101** | Message sender balance is insufficient. | -               |
| **130102** | The token isn't transferable.           | -               |

#### bulkTransfer (1302XX)

| Code       | Situation                                             | Possible causes                                                                                                             | 
|------------|-------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------|
| **130201** | Length of To and of Value aren't matched.             | -                                                                                                                           |
| **130202** | Transfer amount is greater than from address balance. | -                                                                                                                           |
| **130203** | The token isn't transferable.                         | All of following conditions is matched.<br/> - Message sender isn't tradable Exchange.<br/> - The token isn't transferable. |

#### transferFrom (1303XX)

| Code       | Situation                                             | Possible causes | 
|------------|-------------------------------------------------------|-----------------|
| **130301** | Transfer amount is greater than from address balance. | -               |

#### consume (1304XX)

| Code       | Situation                               | Possible causes | 
|------------|-----------------------------------------|-----------------|
| **130401** | Message sender balance is insufficient. | -               |

#### applyForOffering (1305XX)

| Code       | Situation                                                               | Possible causes | 
|------------|-------------------------------------------------------------------------|-----------------|
| **130501** | Offering is stopped.                                                    | -               |
| **130502** | Personal information of message sender isn't registered to token owner. |                 |

#### bulkTransferFrom (1306XX)

| Code       | Situation                                   | Possible causes | 
|------------|---------------------------------------------|-----------------|
| **130601** | The From, To and Value lengths don't match. | -               |

### IbetMembership (14XXXX)

#### transferToContract (1400XX)

| Code       | Situation                                    | Possible causes | 
|------------|----------------------------------------------|-----------------|
| **140001** | Destination address isn't tradable exchange. | -               |

#### transfer (1401XX)

| Code       | Situation                               | Possible causes | 
|------------|-----------------------------------------|-----------------|
| **140101** | Message sender balance is insufficient. | -               |
| **140102** | The token isn't transferable.           | -               |

#### bulkTransfer (1402XX)

| Code       | Situation                                             | Possible causes                                                                                                             | 
|------------|-------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------|
| **140201** | Length of To and of Value aren't matched.             | -                                                                                                                           |
| **140202** | Transfer amount is greater than from address balance. | -                                                                                                                           |
| **140203** | The token isn't transferable.                         | All of following conditions is matched.<br/> - Message sender isn't tradable Exchange.<br/> - The token isn't transferable. |

#### transferFrom (1403XX)

| Code       | Situation                                             | Possible causes | 
|------------|-------------------------------------------------------|-----------------|
| **140301** | Transfer amount is greater than from address balance. | -               |

#### applyForOffering (1404XX)

| Code       | Situation                                                               | Possible causes | 
|------------|-------------------------------------------------------------------------|-----------------|
| **140401** | Offering is stopped.                                                    | -               |
| **140402** | Personal information of message sender isn't registered to token owner. |                 |

#### bulkTransferFrom (1405XX)

| Code       | Situation                                   | Possible causes | 
|------------|---------------------------------------------|-----------------|
| **140501** | The From, To and Value lengths don't match. | -               |

### IbetStandardToken (15XXXX)

#### transferToContract (1500XX)

| Code       | Situation                                    | Possible causes | 
|------------|----------------------------------------------|-----------------|
| **150001** | Destination address isn't tradable exchange. | -               |

#### transfer (1501XX)

| Code       | Situation                               | Possible causes | 
|------------|-----------------------------------------|-----------------|
| **150101** | Message sender balance is insufficient. | -               |

#### bulkTransfer (1502XX)

| Code       | Situation                                             | Possible causes                                                                                                             | 
|------------|-------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------|
| **150201** | Length of To and of Value aren't matched.             | -                                                                                                                           |
| **150202** | Transfer amount is greater than from address balance. | -                                                                                                                           |

#### transferFrom (1503XX)

| Code       | Situation                                             | Possible causes | 
|------------|-------------------------------------------------------|-----------------|
| **150301** | Transfer amount is greater than from address balance. | -               |

#### bulkTransferFrom (1504XX)

| Code       | Situation                                   | Possible causes | 
|------------|---------------------------------------------|-----------------|
| **150401** | The From, To and Value lengths don't match. | -               |

### ExchangeStorage (20XXXX)

#### onlyLatestVersion (2000XX)
| Code       | Situation                                               | Possible causes | 
|------------|---------------------------------------------------------|-----------------|
| **200001** | Message sender(exchange contract) isn't latest version. | -               |

### IbetExchange (21XXXX)

#### createOrder (2100XX)
| Code       | Situation                          | Possible causes                                                                                                                                             | 
|------------|------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **210001** | Create order condition is invalid. | Any of following conditions is matched.<br/> - Amount is 0.<br/> - Token status is false.<br/> Message sender is contract address.<br/> - Agent is invalid. |

#### cancelOrder (2101XX)

| Code       | Situation                              | Possible causes | 
|------------|----------------------------------------|-----------------|
| **210101** | Cancel order ID is invalid.            | -               |
| **210102** | Amount of target order is remaining.   | -               |
| **210103** | Order has already been canceled.       | -               |
| **210104** | Message sender is not the order owner. | -               |

#### forceCancelOrder (2102XX)

| Code       | Situation                              | Possible causes | 
|------------|----------------------------------------|-----------------|
| **210201** | Cancel order ID is invalid.            | -               |
| **210202** | Amount of target order is remaining.   | -               |
| **210203** | Order has already been canceled.       | -               |
| **210204** | Message sender is not the order agent. | -               |

#### executeCancelOrder (2103XX)

| Code       | Situation                           | Possible causes                                                                                                                                                                                                                                                                                                                                      | 
|------------|-------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **210301** | Target order ID is invalid.         | -                                                                                                                                                                                                                                                                                                                                                    |
| **210302** | Execute order condition is invalid. | Any of following conditions is matched<br/> - Amount is 0.<br/> - Take operation side is not matched to original order.<br/> - Message sender is original order owner.<br/> - Message sender is contract address.<br/> - Order has already been canceled.<br/> - Token status is inactive.<br/> - Take amount is greater than original order amount. |

#### confirmAgreement (2104XX)

| Code       | Situation                       | Possible causes                                                                                                                                                             | 
|------------|---------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **210401** | Target order ID is invalid.     | -                                                                                                                                                                           |
| **210402** | Target agreement ID is invalid. | -                                                                                                                                                                           |
| **210403** | Agreement condition is invalid. | Any of following conditions is matched<br/> - Agreement has been already paid.<br/> - Agreement has been already canceled.<br/> - Message sender is not the agent of order. |

#### cancelAgreement (2105XX)

| Code       | Situation                                 | Possible causes                                                                                                                                  | 
|------------|-------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------|
| **210501** | Target order ID is invalid.               | -                                                                                                                                                |
| **210502** | Target agreement ID is invalid.           | -                                                                                                                                                |
| **210503** | Expired agreement condition is invalid.   | Any of following conditions is matched<br/> - Agreement has been already been paid or canceled.<br/> - Message sender is invalid.                |
| **210504** | Unexpired agreement condition is invalid. | Any of following conditions is matched<br/> - Agreement has been already been paid or canceled.<br/> - Message sender is not the agent of order. |

#### withdraw (2106XX)

| Code       | Situation                               | Possible causes | 
|------------|-----------------------------------------|-----------------|
| **210601** | Message sender balance is insufficient. | -               |

### EscrowStorage (22XXXX)

#### onlyLatestVersion (2200XX)
| Code       | Situation                                               | Possible causes | 
|------------|---------------------------------------------------------|-----------------|
| **220001** | Message sender(exchange contract) isn't latest version. | -               |

### IbetEscrow (23XXXX)

#### createEscrow (2300XX)
| Code       | Situation                               | Possible causes | 
|------------|-----------------------------------------|-----------------|
| **230001** | Escrow amount is 0.                     | -               |
| **230002** | Message sender balance is insufficient. | -               |
| **230003** | Token status of escrow is inactive.     | -               |

#### cancelEscrow (2301XX)
| Code       | Situation                                             | Possible causes | 
|------------|-------------------------------------------------------|-----------------|
| **230101** | Target escrow ID is invalid.                          | -               |
| **230102** | Target escrow status is invalid.                      | -               |
| **230103** | Message sender is not escrow sender and escrow agent. | -               |
| **230104** | Token status of escrow is inactive.                   | -               |

#### finishEscrow (2302XX)
| Code       | Situation                           | Possible causes | 
|------------|-------------------------------------|-----------------|
| **230201** | Target escrow ID is invalid.        | -               |
| **230202** | Target escrow status is invalid.    | -               |
| **230203** | Message sender is not escrow agent. | -               |
| **230204** | Token status of escrow is inactive. | -               |

#### withdraw (2303XX)
| Code       | Situation                               | Possible causes | 
|------------|-----------------------------------------|-----------------|
| **230301** | Message sender balance is insufficient. | -               |

### IbetSecurityTokenEscrow (24XXXX)

#### createEscrow (2400XX)
| Code       | Situation                               | Possible causes | 
|------------|-----------------------------------------|-----------------|
| **240001** | Escrow amount is 0.                     | -               |
| **240002** | Message sender balance is insufficient. | -               |
| **240003** | Token status of escrow is inactive.     | -               |

#### cancelEscrow (2401XX)
| Code       | Situation                                             | Possible causes | 
|------------|-------------------------------------------------------|-----------------|
| **240101** | Target escrow ID is invalid.                          | -               |
| **240102** | Target escrow status is invalid.                      | -               |
| **240103** | Message sender is not escrow sender and escrow agent. | -               |
| **240104** | Token status of escrow is inactive.                   | -               |

#### approveTransfer (2402XX)
| Code       | Situation                                   | Possible causes | 
|------------|---------------------------------------------|-----------------|
| **240201** | Application doesn't exist.                  | -               |
| **240202** | Message sender is not token owner.          | -               |
| **240203** | Target escrow status is invalid.            | -               |
| **240204** | Target escrow status has not been finished. | -               |
| **240205** | Token status of escrow is inactive.         | -               |

#### finishEscrow (2403XX)
| Code       | Situation                           | Possible causes | 
|------------|-------------------------------------|-----------------|
| **240301** | Target escrow ID is invalid.        | -               |
| **240302** | Target escrow status is invalid.    | -               |
| **240303** | Message sender is not escrow agent. | -               |
| **240304** | Token status of escrow is inactive. | -               |

#### withdraw (2404XX)
| Code       | Situation                               | Possible causes | 
|------------|-----------------------------------------|-----------------|
| **240401** | Message sender balance is insufficient. | -               |

### DVPStorage (25XXXX)

#### onlyLatestVersion (2500XX)
| Code       | Situation                                               | Possible causes | 
|------------|---------------------------------------------------------|-----------------|
| **250001** | Message sender(exchange contract) isn't latest version. | -               |

### IbetSecurityTokenDVP (26XXXX)

#### createDelivery (2600XX)
| Code       | Situation                                              | Possible causes | 
|------------|--------------------------------------------------------|-----------------|
| **260001** | Delivery amount is 0.                                  | -               |
| **260002** | Message sender balance is insufficient.                | -               |
| **260003** | Token status of delivery is inactive.                  | -               |
| **260004** | Token transferApprovalRequired of delivery is enabled. | -               |

#### cancelDelivery (2601XX)
| Code       | Situation                                                         | Possible causes | 
|------------|-------------------------------------------------------------------|-----------------|
| **260101** | Target delivery ID is invalid.                                    | -               |
| **260102** | Target delivery status is invalid.                                | -               |
| **260103** | Target delivery has been confirmed.                               | -               |
| **260104** | Message sender is not the delivery seller nor the delivery buyer. | -               |

#### confirmDelivery (2602XX)
| Code       | Situation                                              | Possible causes | 
|------------|--------------------------------------------------------|-----------------|
| **260201** | Target delivery ID is invalid.                         | -               |
| **260202** | Target delivery status is invalid.                     | -               |
| **260203** | Target delivery has been confirmed.                    | -               |
| **260204** | Message sender is not the delivery buyer.              | -               |
| **260205** | Token status of delivery is inactive.                  | -               |
| **260206** | Token transferApprovalRequired of delivery is enabled. | -               |

#### finishDelivery (2603XX)
| Code       | Situation                                              | Possible causes | 
|------------|--------------------------------------------------------|-----------------|
| **260301** | Target delivery ID is invalid.                         | -               |
| **260302** | Target delivery status is invalid.                     | -               |
| **260303** | Target delivery has not been confirmed.                | -               |
| **260304** | Message sender is not the delivery agent.              | -               |
| **260305** | Token status of delivery is inactive.                  | -               |
| **260306** | Token transferApprovalRequired of delivery is enabled. | -               |

#### abortDelivery (2604XX)
| Code       | Situation                                 | Possible causes | 
|------------|-------------------------------------------|-----------------|
| **260401** | Target delivery ID is invalid.            | -               |
| **260402** | Target delivery status is invalid.        | -               |
| **260403** | Target delivery has been confirmed.       | -               |
| **260404** | Message sender is not the delivery agent. | -               |

#### withdraw (2605XX)
| Code       | Situation                               | Possible causes | 
|------------|-----------------------------------------|-----------------|
| **260501** | Message sender balance is insufficient. | -               |

#### withdrawPartial (2606XX)
| Code       | Situation                               | Possible causes | 
|------------|-----------------------------------------|-----------------|
| **260601** | Message sender balance is insufficient. | -               |

### PaymentGateway (30XXXX)

#### register (3000XX)
| Code       | Situation                                 | Possible causes | 
|------------|-------------------------------------------|-----------------|
| **300001** | Payment account is banned.                | -               |

#### approve (3001XX)
| Code       | Situation                                 | Possible causes | 
|------------|-------------------------------------------|-----------------|
| **300101** | Target account address is not registered. | -               |

#### warn (3002XX)
| Code       | Situation                                 | Possible causes | 
|------------|-------------------------------------------|-----------------|
| **300201** | Target account address is not registered. | -               |

#### disapprove (3003XX)
| Code       | Situation                                 | Possible causes | 
|------------|-------------------------------------------|-----------------|
| **300301** | Target account address is not registered. | -               |

#### approve (3004XX)
| Code       | Situation                                 | Possible causes | 
|------------|-------------------------------------------|-----------------|
| **300401** | Target account address is not registered. | -               |

#### modify (3005XX)
| Code       | Situation                                 | Possible causes | 
|------------|-------------------------------------------|-----------------|
| **300501** | Target account address is not registered. | -               |

### PersonalInfo (40XXXX)

#### modify (4000XX)
| Code       | Situation                                               | Possible causes | 
|------------|---------------------------------------------------------|-----------------|
| **400001** | Target account address is not registered.               | -               |
| **400002** | Target account address is not linked to message sender. | -               |

### Ownable (50XXXX)

#### onlyOwner (5000XX)
| Code       | Situation                             | Possible causes | 
|------------|---------------------------------------|-----------------|
| **500001** | Message sender is not contract owner. | -               |

#### transferOwnership (5001XX)
| Code       | Situation                     | Possible causes | 
|------------|-------------------------------|-----------------|
| **500101** | New owner address is not set. | -               |

### ContractRegistry (60XXXX)

#### register (6000XX)
| Code       | Situation                               | Possible causes | 
|------------|-----------------------------------------|-----------------|
| **600001** | Target address is not contract address. | -               |
| **600002** | Message sender is not contract owner.   | -               |

### E2EMessaging (61XXXX)

#### getLastMessage (6100XX)
| Code       | Situation                                    | Possible causes | 
|------------|----------------------------------------------|-----------------|
| **610001** | E2E Message for message owner doesn't exist. | -               |

#### clearMessage (6101XX)
| Code       | Situation                                 | Possible causes | 
|------------|-------------------------------------------|-----------------|
| **610011** | Message sender is not E2E Message sender. | -               |

### FreezeLog (62XXXX)

#### getLastMessage (6200XX)
| Code       | Situation      | Possible causes | 
|------------|----------------|-----------------|
| **620001** | Log is frozen. | -               |
