## Error Code
This is a definition list of errors to be thrown when transaction reverts.
Developers will receive error msg as code, and each error code is described below, including description of situation and possible causes.    

### Token Error
- [TokenList (10XX)](#TokenList-(10XX))
- [IbetShare (11XX/12XX)](#IbetShare-(11XX/12XX))
- [IbetStraightBond (13XX/14XX)](#IbetStraightBond-(13XX/14XX))
- [IbetCoupon (15XX)](#IbetCoupon-(15XX))
- [IbetMembership (16XX)](#IbetMembership-(16XX))
- [IbetStandardToken (17XX)](#IbetStandardToken-(17XX))

### Exchange & Escrow Error
- [ExchangeStorage (20XX)](#ExchangeStorage-(20XX))
- [IbetExchange (21XX)](#IbetExchange-(21XX))
- [EscrowStorage (22XX)](#EscrowStorage-(22XX))
- [IbetEscrow (23XX)](#IbetEscrow-(23XX))
- [IbetSecurityTokenEscrow (24XX)](#IbetSecurityTokenEscrow-(24XX))

### Payment Error
- [PaymentGateway (30XX)](#PaymentGateway-(30XX))

### Ledger Error
- [PersonalInfo (40XX)](#PersonalInfo-(40XX))

### Access Error
- [Ownable (50XX)](#Ownable-(50XX))

### Utils Error
- [ContractRegistry (60XX)](#ContractRegistry-(60XX))
- [E2EMessaging (61XX)](#E2EMessaging-(61XX))
- [FreezeLog (62XX)](#FreezeLog-(62XX))

### TokenList (10XX)

#### register (100X)

| Code     | Situation                                | Possible causes | 
|----------|------------------------------------------|-----------------|
| **1001** | The address has already been registered. | -               |
| **1002** | Message sender must be the token owner.  | -               |

#### changeOwner (101X)

| Code     | Situation                               | Possible causes | 
|----------|-----------------------------------------|-----------------|
| **1011** | The address has not been registered.    | -               |
| **1012** | Message sender must be the token owner. | -               |

### IbetShare (11XX/12XX)

#### lock (110X)

| Code     | Situation                                             | Possible causes                                                                                                                      | 
|----------|-------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------|
| **1101** | Lock address is invalid.                              | Any of following conditions is not matched.<br/> - Lock address isn't authorized for locking <br/> - Lock Address isn't token owner. |
| **1102** | Lock amount must be less than message sender balance. | -                                                                                                                                    |

#### unlock (111X)

| Code     | Situation                                      | Possible causes                                                                                                                          | 
|----------|------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------|
| **1111** | Unlock address is invalid.                     | Any of following conditions is not matched.<br/> - Unlock address isn't authorized for locking <br/> - Unlock Address isn't token owner. |
| **1112** | Unlock amount must be less than locked amount. | -                                                                                                                                        |

#### transferToAddress (112X)

| Code     | Situation                            | Possible causes                                                                                                                                                        | 
|----------|--------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **1121** | The token isn't transferable.        | All of following conditions is matched.<br/> - Message sender isn't tradable Exchange.<br/> - Approval is required for the token transferring.                         |
| **1122** | Destination address check is failed. | All of following conditions is matched.<br/> - Destination address isn't token owner.<br/> - Destination address isn't registered personal information to token owner. |

#### transferToContract (113X)

| Code     | Situation                                    | Possible causes | 
|----------|----------------------------------------------|-----------------|
| **1131** | Destination address isn't tradable exchange. | -               |

#### transfer (114X)

| Code     | Situation                               | Possible causes | 
|----------|-----------------------------------------|-----------------|
| **1141** | Message sender balance is insufficient. | -               |
| **1142** | The token isn't transferable.           | -               |

#### bulkTransfer (115X)

| Code     | Situation                                             | Possible causes                                                                                                                                | 
|----------|-------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------|
| **1151** | Transferring of this token requires approval.         | -                                                                                                                                              |
| **1152** | Length of To and of Value aren't matched.             | -                                                                                                                                              |
| **1153** | Transfer amount is greater than from address balance. | -                                                                                                                                              |
| **1154** | The token isn't transferable.                         | All of following conditions is matched.<br/> - Message sender isn't tradable Exchange.<br/> - Approval is required for the token transferring. |

#### transferFrom (116X)

| Code     | Situation                                             | Possible causes | 
|----------|-------------------------------------------------------|-----------------|
| **1161** | Transfer amount is greater than from address balance. | -               |

#### applyForTransfer (117X)

| Code     | Situation                            | Possible causes                                                                                                                                                                                           | 
|----------|--------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **1171** | Apply for transfer is invalid.       | Any of following conditions is matched.<br/> - Approval is not required for the token transferring.<br/> - The token is not transferable.<br/> - Message sender balance is less than transferring amount. |
| **1172** | Destination address check is failed. | All of following conditions is matched.<br/> - Destination address isn't token owner.<br/> - Destination address hasn't registered personal information to token owner.                                   |

#### cancelTransfer (118X)

| Code     | Situation                                      | Possible causes                                                                                                                 | 
|----------|------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------|
| **1181** | Canceling application for transfer is invalid. | All of following conditions is matched.<br/> - Message sender isn't application owner.<br/> - Message sender isn't token owner. |
| **1182** | Application is invalid.                        | -                                                                                                                               |

#### approveTransfer (119X)

| Code     | Situation                 | Possible causes | 
|----------|---------------------------|-----------------|
| **1191** | Token isn't transferable. | -               |
| **1192** | Application is invalid.   | -               |

#### applyForOffering (120X)

| Code     | Situation                                                               | Possible causes | 
|----------|-------------------------------------------------------------------------|-----------------|
| **1201** | Offering is stopped.                                                    | -               |
| **1202** | Personal information of message sender isn't registered to token owner. |                 |

#### redeemFrom (121X)

| Code     | Situation                                          | Possible causes | 
|----------|----------------------------------------------------|-----------------|
| **1211** | Redeem amount is less than locked address balance. | -               |
| **1212** | Redeem amount is less than target address balance. | -               |

### IbetStraightBond (13XX/14XX)

#### lock (130X)

| Code     | Situation                                             | Possible causes                                                                                                                      | 
|----------|-------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------|
| **1301** | Lock address is invalid.                              | Any of following conditions is not matched.<br/> - Lock address isn't authorized for locking <br/> - Lock Address isn't token owner. |
| **1302** | Lock amount must be less than message sender balance. | -                                                                                                                                    |

#### unlock (131X)

| Code     | Situation                                      | Possible causes                                                                                                                          | 
|----------|------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------|
| **1311** | Unlock address is invalid.                     | Any of following conditions is not matched.<br/> - Unlock address isn't authorized for locking <br/> - Unlock Address isn't token owner. |
| **1312** | Unlock amount must be less than locked amount. | -                                                                                                                                        |

#### transferToAddress (132X)

| Code     | Situation                            | Possible causes                                                                                                                                                         | 
|----------|--------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **1321** | The token isn't transferable.        | All of following conditions is matched.<br/> - Message sender isn't tradable Exchange.<br/> - Approval is required for the token transferring.                          |
| **1322** | Destination address check is failed. | All of following conditions is matched.<br/> - Destination address isn't token owner.<br/> - Destination address hasn't registered personal information to token owner. |

#### transferToContract (133X)

| Code     | Situation                                    | Possible causes | 
|----------|----------------------------------------------|-----------------|
| **1331** | Destination address isn't tradable exchange. | -               |

#### transfer (134X)

| Code     | Situation                               | Possible causes | 
|----------|-----------------------------------------|-----------------|
| **1341** | Message sender balance is insufficient. | -               |
| **1342** | The token isn't transferable.           | -               |

#### bulkTransfer (135X)

| Code     | Situation                                             | Possible causes                                                                                                             | 
|----------|-------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------|
| **1351** | Length of To and of Value aren't matched.             | -                                                                                                                           |
| **1352** | Transfer amount is greater than from address balance. | -                                                                                                                           |
| **1353** | The token isn't transferable.                         | All of following conditions is matched.<br/> - Message sender isn't tradable Exchange.<br/> - The token isn't transferable. |

#### transferFrom (136X)

| Code     | Situation                                             | Possible causes | 
|----------|-------------------------------------------------------|-----------------|
| **1361** | Transfer amount is greater than from address balance. | -               |

#### applyForTransfer (137X)

| Code     | Situation                            | Possible causes                                                                                                                                                                                           | 
|----------|--------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **1371** | Apply for transfer is invalid.       | Any of following conditions is matched.<br/> - Approval is not required for the token transferring.<br/> - The token is not transferable.<br/> - Message sender balance is less than transferring amount. |
| **1372** | Destination address check is failed. | All of following conditions is matched.<br/> - Destination address isn't token owner.<br/> - Destination address hasn't registered personal information to token owner.                                   || **a**    |                                        |                                                                                                                                                                                                          |

#### cancelTransfer (138X)

| Code     | Situation                                      | Possible causes                                                                                                                 | 
|----------|------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------|
| **1381** | Canceling application for transfer is invalid. | All of following conditions is matched.<br/> - Message sender isn't application owner.<br/> - Message sender isn't token owner. |
| **1382** | Application is invalid.                        | -                                                                                                                               |

#### approveTransfer (139X)

| Code     | Situation                 | Possible causes | 
|----------|---------------------------|-----------------|
| **1391** | Token isn't transferable. | -               |
| **1392** | Application is invalid.   | -               |

#### applyForOffering (140X)

| Code     | Situation                                                               | Possible causes | 
|----------|-------------------------------------------------------------------------|-----------------|
| **1401** | Offering is stopped.                                                    | -               |
| **1402** | Personal information of message sender isn't registered to token owner. |                 |

#### redeemFrom (141X)

| Code     | Situation                                          | Possible causes | 
|----------|----------------------------------------------------|-----------------|
| **1411** | Redeem amount is less than locked address balance. | -               |
| **1412** | Redeem amount is less than target address balance. | -               |

### IbetCoupon (15XX)

#### transferToContract (150X)

| Code     | Situation                                    | Possible causes | 
|----------|----------------------------------------------|-----------------|
| **1501** | Destination address isn't tradable exchange. | -               |

#### transfer (151X)

| Code     | Situation                               | Possible causes | 
|----------|-----------------------------------------|-----------------|
| **1511** | Message sender balance is insufficient. | -               |
| **1512** | The token isn't transferable.           | -               |

#### bulkTransfer (152X)

| Code     | Situation                                             | Possible causes                                                                                                             | 
|----------|-------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------|
| **1521** | Length of To and of Value aren't matched.             | -                                                                                                                           |
| **1522** | Transfer amount is greater than from address balance. | -                                                                                                                           |
| **1523** | The token isn't transferable.                         | All of following conditions is matched.<br/> - Message sender isn't tradable Exchange.<br/> - The token isn't transferable. |

#### transferFrom (153X)

| Code     | Situation                                             | Possible causes | 
|----------|-------------------------------------------------------|-----------------|
| **1531** | Transfer amount is greater than from address balance. | -               |

#### consume (154X)

| Code     | Situation                               | Possible causes | 
|----------|-----------------------------------------|-----------------|
| **1541** | Message sender balance is insufficient. | -               |

#### applyForOffering (155X)

| Code     | Situation                                                               | Possible causes | 
|----------|-------------------------------------------------------------------------|-----------------|
| **1551** | Offering is stopped.                                                    | -               |
| **1552** | Personal information of message sender isn't registered to token owner. |                 |

### IbetMembership (16XX)

#### transferToContract (160X)

| Code     | Situation                                    | Possible causes | 
|----------|----------------------------------------------|-----------------|
| **1601** | Destination address isn't tradable exchange. | -               |

#### transfer (161X)

| Code     | Situation                               | Possible causes | 
|----------|-----------------------------------------|-----------------|
| **1611** | Message sender balance is insufficient. | -               |
| **1612** | The token isn't transferable.           | -               |

#### bulkTransfer (162X)

| Code     | Situation                                             | Possible causes                                                                                                             | 
|----------|-------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------|
| **1621** | Length of To and of Value aren't matched.             | -                                                                                                                           |
| **1622** | Transfer amount is greater than from address balance. | -                                                                                                                           |
| **1623** | The token isn't transferable.                         | All of following conditions is matched.<br/> - Message sender isn't tradable Exchange.<br/> - The token isn't transferable. |

#### transferFrom (163X)

| Code     | Situation                                             | Possible causes | 
|----------|-------------------------------------------------------|-----------------|
| **1631** | Transfer amount is greater than from address balance. | -               |

#### applyForOffering (164X)

| Code     | Situation                                                               | Possible causes | 
|----------|-------------------------------------------------------------------------|-----------------|
| **1641** | Offering is stopped.                                                    | -               |
| **1642** | Personal information of message sender isn't registered to token owner. |                 |

### IbetStandardToken (17XX)

#### transferToContract (170X)

| Code     | Situation                                    | Possible causes | 
|----------|----------------------------------------------|-----------------|
| **1701** | Destination address isn't tradable exchange. | -               |

#### transfer (171X)

| Code     | Situation                               | Possible causes | 
|----------|-----------------------------------------|-----------------|
| **1711** | Message sender balance is insufficient. | -               |

#### bulkTransfer (172X)

| Code     | Situation                                             | Possible causes                                                                                                             | 
|----------|-------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------|
| **1721** | Length of To and of Value aren't matched.             | -                                                                                                                           |
| **1722** | Transfer amount is greater than from address balance. | -                                                                                                                           |

#### transferFrom (173X)

| Code     | Situation                                             | Possible causes | 
|----------|-------------------------------------------------------|-----------------|
| **1731** | Transfer amount is greater than from address balance. | -               |

### ExchangeStorage (20XX)

#### onlyLatestVersion (200X)
| Code     | Situation                                               | Possible causes | 
|----------|---------------------------------------------------------|-----------------|
| **2001** | Message sender(exchange contract) isn't latest version. | -               |

### IbetExchange (21XX)

#### createOrder (210X)
| Code     | Situation                          | Possible causes                                                                                                                                             | 
|----------|------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **2101** | Create order condition is invalid. | Any of following conditions is matched.<br/> - Amount is 0.<br/> - Token status is false.<br/> Message sender is contract address.<br/> - Agent is invalid. |

#### cancelOrder (211X)

| Code     | Situation                              | Possible causes | 
|----------|----------------------------------------|-----------------|
| **2111** | Cancel order ID is invalid.            | -               |
| **2112** | Amount of target order is remaining.   | -               |
| **2113** | Order has already been canceled.       | -               |
| **2114** | Message sender is not the order owner. | -               |

#### forceCancelOrder (212X)

| Code     | Situation                              | Possible causes | 
|----------|----------------------------------------|-----------------|
| **2121** | Cancel order ID is invalid.            | -               |
| **2122** | Amount of target order is remaining.   | -               |
| **2123** | Order has already been canceled.       | -               |
| **2124** | Message sender is not the order agent. | -               |

#### executeCancelOrder (213X)

| Code     | Situation                           | Possible causes                                                                                                                                                                                                                                                                                                                                      | 
|----------|-------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **2131** | Target order ID is invalid.         | -                                                                                                                                                                                                                                                                                                                                                    |
| **2132** | Execute order condition is invalid. | Any of following conditions is matched<br/> - Amount is 0.<br/> - Take operation side is not matched to original order.<br/> - Message sender is original order owner.<br/> - Message sender is contract address.<br/> - Order has already been canceled.<br/> - Token status is inactive.<br/> - Take amount is greater than original order amount. |

#### confirmAgreement (214X)

| Code     | Situation                       | Possible causes                                                                                                                                                             | 
|----------|---------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **2141** | Target order ID is invalid.     | -                                                                                                                                                                           |
| **2142** | Target agreement ID is invalid. | -                                                                                                                                                                           |
| **2143** | Agreement condition is invalid. | Any of following conditions is matched<br/> - Agreement has been already paid.<br/> - Agreement has been already canceled.<br/> - Message sender is not the agent of order. |

#### cancelAgreement (215X)

| Code     | Situation                                 | Possible causes                                                                                                                                  | 
|----------|-------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------|
| **2151** | Target order ID is invalid.               | -                                                                                                                                                |
| **2152** | Target agreement ID is invalid.           | -                                                                                                                                                |
| **2153** | Expired agreement condition is invalid.   | Any of following conditions is matched<br/> - Agreement has been already been paid or canceled.<br/> - Message sender is invalid.                |
| **2154** | Unexpired agreement condition is invalid. | Any of following conditions is matched<br/> - Agreement has been already been paid or canceled.<br/> - Message sender is not the agent of order. |

#### withdraw (216X)

| Code     | Situation                               | Possible causes | 
|----------|-----------------------------------------|-----------------|
| **2161** | Message sender balance is insufficient. | -               |

### EscrowStorage (22XX)

#### onlyLatestVersion (220X)
| Code     | Situation                                               | Possible causes | 
|----------|---------------------------------------------------------|-----------------|
| **2201** | Message sender(exchange contract) isn't latest version. | -               |

### IbetEscrow (23XX)

#### createEscrow (230X)
| Code     | Situation                               | Possible causes | 
|----------|-----------------------------------------|-----------------|
| **2301** | Escrow amount is 0.                     | -               |
| **2302** | Message sender balance is insufficient. | -               |
| **2303** | Token status of escrow is inactive.     | -               |


#### cancelEscrow (231X)
| Code     | Situation                                             | Possible causes | 
|----------|-------------------------------------------------------|-----------------|
| **2311** | Target escrow ID is invalid.                          | -               |
| **2312** | Target escrow status is invalid.                      | -               |
| **2313** | Message sender is not escrow sender and escrow agent. | -               |
| **2314** | Token status of escrow is inactive.                   | -               |

#### finishEscrow (232X)
| Code     | Situation                           | Possible causes | 
|----------|-------------------------------------|-----------------|
| **2321** | Target escrow ID is invalid.        | -               |
| **2322** | Target escrow status is invalid.    | -               |
| **2323** | Message sender is not escrow agent. | -               |
| **2324** | Token status of escrow is inactive. | -               |

#### withdraw (233X)
| Code     | Situation                               | Possible causes | 
|----------|-----------------------------------------|-----------------|
| **2331** | Message sender balance is insufficient. | -               |

### IbetSecurityTokenEscrow (24XX)

#### createEscrow (240X)
| Code     | Situation                               | Possible causes | 
|----------|-----------------------------------------|-----------------|
| **2401** | Escrow amount is 0.                     | -               |
| **2402** | Message sender balance is insufficient. | -               |
| **2403** | Token status of escrow is inactive.     | -               |

#### cancelEscrow (241X)
| Code     | Situation                                             | Possible causes | 
|----------|-------------------------------------------------------|-----------------|
| **2411** | Target escrow ID is invalid.                          | -               |
| **2412** | Target escrow status is invalid.                      | -               |
| **2413** | Message sender is not escrow sender and escrow agent. | -               |
| **2414** | Token status of escrow is inactive.                   | -               |

#### approveTransfer (242X)
| Code     | Situation                                   | Possible causes | 
|----------|---------------------------------------------|-----------------|
| **2421** | Application doesn't exist.                  | -               |
| **2422** | Message sender is not token owner.          | -               |
| **2423** | Target escrow status is invalid.            | -               |
| **2423** | Target escrow status has not been finished. | -               |
| **2425** | Token status of escrow is inactive.         | -               |

#### finishEscrow (243X)
| Code     | Situation                           | Possible causes | 
|----------|-------------------------------------|-----------------|
| **2431** | Target escrow ID is invalid.        | -               |
| **2432** | Target escrow status is invalid.    | -               |
| **2433** | Message sender is not escrow agent. | -               |
| **2434** | Token status of escrow is inactive. | -               |

#### withdraw (244X)
| Code     | Situation                               | Possible causes | 
|----------|-----------------------------------------|-----------------|
| **2441** | Message sender balance is insufficient. | -               |

### PaymentGateway (30XX)

#### register (300X)
| Code     | Situation                                 | Possible causes | 
|----------|-------------------------------------------|-----------------|
| **3001** | Payment account is banned.                | -               |


#### approve (301X)
| Code     | Situation                                 | Possible causes | 
|----------|-------------------------------------------|-----------------|
| **3011** | Target account address is not registered. | -               |

#### warn (302X)
| Code     | Situation                                 | Possible causes | 
|----------|-------------------------------------------|-----------------|
| **3021** | Target account address is not registered. | -               |

#### disapprove (303X)
| Code     | Situation                                 | Possible causes | 
|----------|-------------------------------------------|-----------------|
| **3031** | Target account address is not registered. | -               |

#### approve (304X)
| Code     | Situation                                 | Possible causes | 
|----------|-------------------------------------------|-----------------|
| **3041** | Target account address is not registered. | -               |

#### modify (305X)
| Code     | Situation                                 | Possible causes | 
|----------|-------------------------------------------|-----------------|
| **3051** | Target account address is not registered. | -               |

### PersonalInfo (40XX)

#### modify (400X)
| Code     | Situation                                               | Possible causes | 
|----------|---------------------------------------------------------|-----------------|
| **4001** | Target account address is not registered.               | -               |
| **4002** | Target account address is not linked to message sender. | -               |

### Ownable (50XX)

#### onlyOwner (500X)
| Code     | Situation                             | Possible causes | 
|----------|---------------------------------------|-----------------|
| **5001** | Message sender is not contract owner. | -               |

#### transferOwnership (501X)
| Code     | Situation                     | Possible causes | 
|----------|-------------------------------|-----------------|
| **5011** | New owner address is not set. | -               |

### ContractRegistry (60XX)

#### register (600X)
| Code     | Situation                               | Possible causes | 
|----------|-----------------------------------------|-----------------|
| **6001** | Target address is not contract address. | -               |
| **6002** | Message sender is not contract owner.   | -               |

### E2EMessaging (61XX)

#### getLastMessage (610X)
| Code     | Situation                                    | Possible causes | 
|----------|----------------------------------------------|-----------------|
| **6101** | E2E Message for message owner doesn't exist. | -               |

#### clearMessage (611X)
| Code     | Situation                                 | Possible causes | 
|----------|-------------------------------------------|-----------------|
| **6111** | Message sender is not E2E Message sender. | -               |

### FreezeLog (62XX)

#### getLastMessage (620X)
| Code     | Situation      | Possible causes | 
|----------|----------------|-----------------|
| **6201** | Log is frozen. | -               |
