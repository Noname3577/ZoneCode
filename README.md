คุณสามารถใช้ Bitkub Online Co., Ltd. API (จาก repo “bitkub‑official‑api‑docs”) เพื่อ **รับค่าข้อมูล** (public endpoints) และ **ส่งคำสั่ง/ข้อมูล** (private endpoints) ไปยังเว็บแอปที่คุณจะสร้างได้ครับ โดยผมสรุปส่วนต่าง ๆ ที่น่าสนใจ พร้อมแบ่งให้เป็นหัวข้อย่อยเพื่อคุณจะเอาไปออกแบบเว็บได้ง่ายขึ้น:

---

## สิ่งที่สามารถ “รับค่า” (Read / GET)

1. Server time

   * Endpoint: `GET /api/servertime` → ใช้ตรวจว่า server-time กับ client sync กันหรือไม่. ([api.bitkub.com][1])
2. Market data (public)

   * เช่น trading pairs / ticker / bids / asks / depth / trades. ([api.bitkub.com][1])
   * ตัวอย่าง: `GET /api/market/ticker` → คืนข้อมูลราคา “last”, “volume”, “percentChange” เป็นต้น. ([api.bitkub.com][2])
3. Crypto API (v4) – รับข้อมูลเกี่ยวกับ coins, deposit history, withdraw history, ฯลฯ → ตัวอย่าง: `GET /api/v4/crypto/coins` เป็นต้น. ([api.bitkub.com][3])
4. Private endpoints (เมื่อใช้ Authentication) – รับข้อมูลของบัญชีผู้ใช้ เช่น wallet balance, open orders, order history เป็นต้น. (ต้องมี key + signature) → ดูหัวข้อ Authentication ด้านล่าง. ([api.bitkub.com][1])

---

## สิ่งที่สามารถ “ส่งค่า” (Write / POST)

1. Place order / cancel order / balances – ตัวอย่าง: `POST /api/market/place-bid` เพื่อส่งคำสั่งซื้อ → ต้องใช้ authentication และ signature. ([api.bitkub.com][1])
2. Crypto API v4 – เช่น ฝาก / ถอน (withdraw) / สร้าง address / ฯลฯ → ตัวอย่าง: `POST /api/v4/crypto/addresses` หรือ `POST /api/v4/crypto/withdraws` เป็นต้น. ([api-jp.bitkub.com][4])
3. คุณต้องเตรียม API Key + Secret พร้อมวิธีคำนวณ signature ให้ถูกตาม spec. (ดูหัวข้อ Authentication)

---

## ส่วนย่อยที่คุณอาจออกแบบในเว็บได้

ผมแบ่งเป็นโมดูลย่อย ๆ ให้คุณเอาไปใช้สร้างหน้าเว็บ หรือส่วน frontend/backend ได้เลย:

### โมดูล A: ข้อมูลตลาด (Market Data)

* แสดงรายการคู่เหรียญ (symbol list)
* แสดงราคาล่าสุด (last price), เปอร์เซนต์เปลี่ยน (percentChange)
* แสดง depth / bids / asks สำหรับคู่เหรียญที่เลือก
* แสดงกราฟ (คุณอาจดึงจาก depth/trades แล้ววาดกราฟเอง)
* ตัวอย่างการเรียก: `GET /api/market/ticker`

### โมดูล B: ข้อมูลบัญชีผู้ใช้ (ต้อง login / API Key)

* แสดงยอดเงินคงเหลือ (wallet)
* แสดงคำสั่งเปิดอยู่ (open orders)
* แสดงประวัติการซื้อขาย (order history)
* แสดงประวัติฝาก-ถอน (สำหรับ crypto API)
* ต้องใช้ endpoint ที่มี authentication

### โมดูล C: ส่งคำสั่ง/จัดการคำสั่งซื้อขาย

* หน้าเว็บให้ผู้ใช้เลือกคู่เหรียญ, ใส่จำนวน, ราคาที่ต้องการ, ประเภทคำสั่ง (limit/market)
* ส่งคำสั่งซื้อ (`POST /api/market/place‐bid` หรือ `place‐ask`)
* ยกเลิกคำสั่ง (`POST /api/market/cancel‐order`)
* ตรวจสอบผลลัพธ์ – แสดงสถานะคำสั่ง, ข้อผิดพลาด

### โมดูล D: ฝาก-ถอน / Crypto Address Management

* แสดงที่อยู่ฝากเงิน (create new address)
* แสดงประวัติการฝาก/ถอน
* ส่งคำดคั่งถอน (withdraw) – ต้องใช้ network/chain ให้ถูกต้องตาม spec. ([‎ Bitkub Exchange][5])
* แสดงข้อมูลเหรียญ (coins) ที่รองรับ

### โมดูล E: ระบบพื้นฐาน

* Authentication (เก็บ API Key + Secret, signature generation)
* ตรวจสอบ timestamp / sync กับ server time
* จัดการ Rate-limit / error handling (ดู errors list)
* UI/UX: แจ้งข้อผิดพลาดให้ผู้ใช้ เช่น Invalid key, signature failed, invalid timestamp. ([api.bitkub.com][6])

---

## ประเด็นที่ควรระวัง

* อย่าเผย API Secret ในฝั่ง client/browser – ให้เรียกผ่าน backend เพื่อความปลอดภัย
* ตรวจสอบให้ timestamp ตรง / server time sync เพื่อหลีกเลี่ยง error “Invalid timestamp”. ([api.bitkub.com][6])
* ตรวจสอบให้เครือข่าย (network) ของเหรียญถูกเมื่อฝาก/ถอน (เช่น ERC-20 = “ETH”, BEP-20 = “BSC”) → ถ้าผิดอาจสูญเงินได้. ([‎ Bitkub Exchange][5])
* ปฏิบัติตามเงื่อนไขของ Bitkub และ rate limit เพื่อไม่ให้โดน block

---

ถ้าคุณอยาก ผมสามารถ **ดึงรายการ endpoint ทั้งหมด** ของ REST API (v3 + v4) พร้อมตัวอย่างโค้ด (JavaScript/Python) ให้ เพื่อใช้เป็นแนวทางในการทำเว็บได้ — คุณอยากให้ผมทำไหมครับ?

[1]: https://api.bitkub.com/docs?utm_source=chatgpt.com "Bitkub API Documentation"
[2]: https://api.bitkub.com/?utm_source=chatgpt.com "Bitkub API Documentation"
[3]: https://api.bitkub.com/docs/endpoint/api/v4/crypto/coins?method=GET&utm_source=chatgpt.com "Coins"
[4]: https://api-jp.bitkub.com/docs/endpoint/api/v4/crypto/addresses?method=POST&utm_source=chatgpt.com "Addresses"
[5]: https://support.bitkub.com/en/support/solutions/articles/151000033093-api-definition-and-application?utm_source=chatgpt.com "API: Definition and application"
[6]: https://api.bitkub.com/docs/authentication?utm_source=chatgpt.com "Authentication"

--------------------------------------------------------------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------------------------------------------------------------------------

เยี่ยม — ด้านล่างผมแจกแบบละเอียดแบบเป็นโมดูลย่อย ๆ (ทั้งหน้าจอ UI, API call ที่ต้องใช้, ฟิลด์สำคัญ, ตัวอย่าง payload, งานฝั่ง backend, โครงสร้างฐานข้อมูลที่แนะนำ, และข้อควรระวัง) — คุณสามารถนำแต่ละหัวข้อไปทำเป็นหน้าเว็บหรือคอมโพเนนต์ได้ทันที

> หมายเหตุ: endpoints ที่ผมเขียนด้านล่างใช้ชื่อเชิงตัวอย่างตามเอกสารทั่วไปของ Bitkub (เช่น `/api/market/ticker`, `/api/market/place-bid`) — ให้ปรับตาม spec จริงใน repo ที่คุณใช้ก่อน deploy

---

# โมดูล A — ข้อมูลตลาด (Market Data / Market Feed)

วัตถุประสงค์: แสดงข้อมูลราคาแบบเรียลไทม์, depth, ประวัติการเทรด และกราฟ

### หน้าจอ / คอมโพเนนต์

* Market Overview (ตารางเหรียญ / สัญลักษณ์)
* Symbol Detail (Header: symbol, last price, 24h change, 24h volume)
* Order Book (Bids / Asks)
* Recent Trades (trade history feed)
* Chart (candlestick / volume)
* Search / Filter / Favorites

### API ที่ใช้ (ตัวอย่าง)

* `GET /api/market/ticker` — ดึง ticker สำหรับทุกคู่ (หรือ `/ticker?symbol=KBETH_BTC` แบบเฉพาะ)
* `GET /api/market/depth?symbol=SYM&limit=50` — ดึง orderbook
* `GET /api/market/trades?symbol=SYM&limit=100` — ดึง recent trades
* `GET /api/servertime` — ซิงค์เวลา (timestamp)

### ฟิลด์สำคัญ (ตัวอย่าง response)

* ticker: `{ symbol, last, high, low, baseVolume, quoteVolume, percentChange }`
* depth: `{ bids: [[price, amount],...], asks: [[price, amount],...] }`
* trade: `{ id, price, amount, side('buy'|'sell'), timestamp }`

### UI states & UX

* Loading, reconnecting (websocket), empty state, error (rate-limit)
* Toggle depth aggregation levels (0.1%, 0.5%)
* Real-time update: ใช้ WebSocket หรือ poll (เช่น 1s)

### Backend responsibilities

* Proxy calls (cache heavy endpoints), aggregate multiple API responses, rate-limit per client
* Convert/expose simplified API ให้ frontend (e.g., `/api/ui/market/ticker`)

### Suggested DB (ถ้าจำเป็น)

* `symbols(symbol, base, quote, listed_at)`
* `market_snapshots(symbol, timestamp, last, high, low, volume)`

### ข้อควรระวัง

* อย่าเก็บ API Secret ใน client
* ใช้ caching สำหรับ ticker/market lists (TTL ~1–10s)
* หากใช้ WebSocket ให้จัด reconnect/backoff

---

# โมดูล B — หน้าแสดงบัญชีผู้ใช้ / Wallet (ต้อง auth)

วัตถุประสงค์: แสดงยอดเงิน, สถานะ portfolio, ประวัติคำสั่งซื้อขาย และประวัติฝาก-ถอน

### หน้าจอ / คอมโพเนนต์

* Dashboard ยอดเงินรวม (Total Balance, breakdown by currency)
* Wallet list (แต่ละเหรียญ: available, locked, total)
* Order history (filter by symbol / status / date range)
* Deposit / Withdraw history

### API ที่ใช้ (private, ต้องมี API key)

* `POST /api/servertime` หรือ `GET /api/servertime` (เพื่อ compute signature / timestamp)
* `POST /api/user/wallet`  (ตัวอย่าง) — ดึง balances
* `POST /api/market/open-orders` — ดึง open orders
* `POST /api/market/order-history` — ประวัติการสั่งซื้อขาย
* `POST /api/v4/crypto/withdraws` / `GET /api/v4/crypto/deposits` — ฝาก/ถอน (v4)

### ฟิลด์สำคัญ

* wallet: `{ coin, available, reserved, total }`
* order: `{ orderId, symbol, side, type, price, amount, filled, status, createdAt }`
* deposit/withdraw: `{ txId, coin, amount, status, address, createdAt }`

### Backend responsibilities

* เก็บ API key/secret แบบเข้ารหัส (vault / env) — **ไม่เก็บ plaintext**
* สร้าง signature และเรียก private endpoints ในนามผู้ใช้
* เก็บ log คำสั่ง (audit) และ mapping user -> API key *ถ้ามี*

### DB (ตารางแนะนำ)

* `users(id, email, hashed_pw, preferences)`
* `user_api_keys(user_id, api_key_id, encrypted_secret, created_at)`
* `user_wallet_snapshots(user_id, coin, available, reserved, total, timestamp)`
* `user_orders(user_id, order_id, symbol, side, price, amount, status, created_at)`

### UI states & UX

* แสดงสถานะ sync (last updated)
* ข้อความเตือนเมื่อยอดเปลี่ยนหรือมีคำสั่ง filled
* ปุ่ม “refresh” + auto refresh (30s–60s) หรือ push notifications

### ข้อควรระวัง

* ต้อง validate permission ก่อนแสดงข้อมูลของ user
* Rate-limiting ของ Bitkub — อย่าให้ user spam refresh

---

# โมดูล C — วางคำสั่งซื้อขาย (Trading UI)

วัตถุประสงค์: ให้ user สร้างคำสั่งซื้อ/ขาย (limit / market), ดูสถานะ, ยกเลิกคำสั่ง

### หน้าจอ / คอมโพเนนต์

* Trade panel (Buy / Sell tabs)

  * Input: price, amount, total (auto-calc)
  * Type: market / limit
  * Leverage? (ถ้า exchange รองรับ) — ถ้าไม่รองรับ ให้ซ่อน
* Active orders list + cancel button
* Order confirmation modal (show fees, estimated total)

### API ที่ใช้ (private)

* `POST /api/market/place-bid` หรือ `POST /api/market/place-ask` — ส่งคำสั่ง
* `POST /api/market/cancel-order` — ยกเลิกคำสั่ง
* `POST /api/market/open-orders` — ดึงคำสั่งเปิดอยู่

### ตัวอย่าง request/response (ตัวอย่าง)

**Place order (limit buy)**
Request:

```json
POST /api/market/place-bid
{
  "sym": "KUB_BTC",
  "amount": "10",
  "price": "0.00001234",
  "type": "limit"
}
```

Response (success):

```json
{ "status": "success", "orderId": "1234567", "filled": "0" }
```

### Backend responsibilities

* Validate user balance ก่อนส่งคำสั่ง (optional: optimistic UI)
* Calculate fees, slippage estimation (for market orders)
* Queue or retry logic for transient errors

### UI states & UX

* Disabled when insufficient balance
* Show pending → filled → partial filled transitions
* Clear error messages from API (e.g., invalid price, insufficient funds, invalid timestamp)

### DB

* `user_orders` table (เก็บทุกคำสั่ง, status history)
* `order_events(order_id, event, timestamp)`

### ข้อควรระวัง

* อย่าให้ client ส่งคำสั่งตรงไปยัง exchange — route ผ่าน backend
* ตรวจสอบ double-submit (disable button / idempotency key)

---

# โมดูล D — ฝาก-ถอน Crypto (Deposit / Withdraw)

วัตถุประสงค์: แสดง address ฝาก, สร้างคำสั่งถอน และแสดงสถานะ

### หน้าจอ / คอมโพเนนต์

* Deposit page: แสดง address, QR code, deposit instructions per coin
* Withdraw page: ฟอร์มใส่ address, amount, select network, 2FA confirmation
* History page: แสดงรายการฝาก-ถอน พร้อมสถานะ

### API ที่ใช้ (โดยมาก private, v4)

* `GET /api/v4/crypto/addresses?coin=COIN` — ดึง/สร้าง deposit address
* `POST /api/v4/crypto/withdraws` — สร้าง withdraw (ต้องตรวจ security)
* `GET /api/v4/crypto/deposits` — ดึงประวัติฝาก

### ฟิลด์สำคัญ

* address object: `{ coin, network, address, createdAt, memo? }`
* withdraw request: `{ coin, network, address, amount, fee, note }`
* status: `pending | processing | completed | rejected`

### Backend responsibilities

* Validate destination address format (เบื้องต้น) — แต่การ validate เชิงลึกขึ้นกับ chain
* Apply 2FA / email confirmation before withdraw
* Log withdraw requests and reconcile with exchange callbacks

### DB

* `crypto_addresses(user_id, coin, network, address, created_at)`
* `withdraws(user_id, withdraw_id, coin, network, amount, fee, address, status, created_at)`

### ข้อควรระวังสำคัญ

* การเลือก network ผิด = สูญเสียเงิน → ต้องแสดงคำเตือนชัดเจน
* ถอนต้องมีการยืนยัน (2FA / email) และ throttle withdrawal rate per user
* ไม่เก็บ private keys / mnemonic ในระบบของคุณ (หากคุณไม่ได้เป็น wallet provider จริง ๆ)

---

# โมดูล E — ระบบพื้นฐาน (Auth, Security, Admin, Logging)

วัตถุประสงค์: ทำให้ระบบปลอดภัย เสถียร และตรวจสอบได้

### Authentication & Authorization

* Frontend: user login (email/password) + optional OAuth
* Backend: store user API key metadata if user links own exchange API (encrypt secret)
* 2FA (TOTP) สำหรับดำเนินการสำคัญ (withdraw, change API key)

### Signature & Time Sync

* เก็บ secret ใน vault (KMS) หรือเข้ารหัสใน DB
* ทุกคำขอไปยัง Bitkub ต้องมี signature: สร้างจาก secret + timestamp ตาม spec
* Sync server time ก่อนเรียก private endpoints

### Rate limiting & Queuing

* Global per-user rate limits; queue requests to avoid hitting exchange rate-limit
* Retry logic with exponential backoff for transient HTTP errors

### Error handling & UX

* Map exchange error codes → ข้อความไทยสำหรับผู้ใช้
* Audit logs: เก็บ request/response ของ private calls ไว้ชั่วคราว (เข้ารหัส)
* Alerting (Slack/email) เมื่อมี repeated failures or withdrawal rejects

### Admin Panel

* ดู logs, user activity, pending withdrawals
* Manual review / KYC statuses (ถ้าระบบของคุณต้องการ)
* Ability to pause system / block malicious IPs

### Database & Data Retention

* Keep minimal sensitive data; store snapshots for reconciliation (30–90 วันตามนโยบาย)
* Scheduled jobs: sync balances, reconcile withdrawals, archive old orders

---

# โมดูล F — UI Components / Frontend Structure (แยกย่อย)

รายการคอมโพเนนต์ที่ควรมี (reuseable)

* Header (market selector, user menu)
* SymbolTickerCard (ใช้ใน list)
* OrderBook (bids/asks columns)
* TradeFeed (real-time scroll)
* TradeForm (buy/sell form)
* BalanceCard
* ModalConfirm (generic)
* Notification/Toast (success/error)
* LoadingSpinner / Skeleton

---

# โมดูล G — Workflows (Flow ตัวอย่าง)

### วางคำสั่ง (user)

1. User เปิด TradeForm → เลือก symbol, ใส่ amount, price
2. Frontend validate inputs → ส่ง POST → backend สร้าง signature → ส่งไปที่ exchange
3. Exchange ตอบกลับ orderId → backend บันทึก → frontend แจ้งผู้ใช้

### ถอน (user)

1. User กด Withdraw → ใส่ address, amount
2. Frontend แสดง warning เครือข่าย → user ยืนยันด้วย OTP
3. Backend เก็บ request → ส่งไป exchange → monitor status → update user

---

# ตัวอย่างโครงสร้างไฟล์ / routes (Backend)

* `routes/api/market.js` — public market endpoints proxy & caching
* `routes/api/user.js` — wallet, orders (private, requires auth)
* `services/bitkubClient.js` — encapsulate signature, requests, retries
* `jobs/syncBalances.js` — cron job sync wallet balances
* `db/models/*` — users, orders, withdraws, snapshots
* `middleware/rateLimiter.js`, `middleware/auth.js`

---

# การออกแบบฐานข้อมูล (ย่อ)

ตารางหลัก ๆ:

* `users`
* `user_api_keys` (encrypted_secret, permissions)
* `user_wallet_snapshots`
* `user_orders`
* `order_events`
* `crypto_addresses`
* `withdraws`
* `audit_logs`

---

# ความปลอดภัย & operational checklist (สำคัญ)

1. เก็บ API Secret แบบเข้ารหัส / ใช้ KMS
2. Backend เป็นตัวกลางในการเรียก exchange (no secrets on client)
3. Implement rate-limiting และ idempotency keys สำหรับการ place-order
4. 2FA สำหรับ withdraw / sensitive actions
5. Validate network/coin mapping ก่อนถอน
6. Log, monitor, alert on errors/failures
7. สื่อสารข้อความผิดพลาดชัดเจนและเป็นมิตรต่อผู้ใช้ (ไทย)
8. เตรียมแผนรับมือกรณี exchange down (circuit breaker)

---

# ตัวอย่าง UI wireframe แบบย่อ (หน้าแรก)

* Topbar: Logo | Search symbol | Wallet (balance) | User menu
* Left column: Symbols list (filter + favorites)
* Center: Chart (candles) + TradeFeed
* Right column: TradeForm (Buy/Sell) + OrderBook
* Bottom: Recent trades + open orders table

---

# ข้อเสนอแนะการพัฒนา (ลำดับขั้น)

1. ทำ Market Data (public) + symbol list + chart (MVP)
2. เพิ่ม TradeForm (simulate orders) — local only (no real place)
3. Implement backend auth + private wallet read (display balances)
4. Add place-order flow + cancel (with real API keys in backend)
5. Add deposit/withdraw with 2FA + admin tooling

---

ถ้าคุณอยาก ผมจะต่อให้เป็น **(A)** ตาราง endpoint ทั้งหมดพร้อมตัวอย่าง request/response ปรับตาม repo จริง หรือ **(B)** ตัวอย่างโค้ด backend (Node.js / Express) สำหรับ proxy พื้นฐานที่สร้าง signature และเรียก Bitkub ให้ — คุณอยากให้ผมทำส่วนไหนต่อเป็นลำดับถัดไป?
===================================================================================================================================================================================

ยอดเยี่ยมครับ — ด้านล่างนี้คือ **Prompt เวอร์ชันสมบูรณ์** ที่คุณสามารถนำไปสั่งให้ AI (เช่น Google Studio Code, Replit, v0.dev, หรือ ChatGPT โหมด Developer) สร้างเว็บระบบเทรด Bitkub ให้โดยอัตโนมัติได้เลย

ผมจัดไว้เป็นภาษาไทย + โครงสร้างชัดเจน ครอบคลุมทุกโมดูลที่เว็บคุณต้องมี (Market / Wallet / Order / Withdraw / Admin ฯลฯ)

---

## 🧠 **Prompt สำหรับให้ AI สร้างเว็บ Bitkub Trading Dashboard**

```
สร้างเว็บไซต์ระบบเทรด Bitkub แบบ Dashboard เต็มระบบ โดยใช้ React (Next.js หรือ Vite ก็ได้) + TailwindCSS + Node.js (Express) สำหรับ backend  

ให้ระบบมีโครงสร้างและฟังก์ชันดังนี้  

---

### 💡 โครงสร้างหลักของเว็บ
1. หน้าเว็บหลัก (Dashboard)
   - แสดงรายการคู่เหรียญทั้งหมด (symbol, last price, 24h change, volume)
   - มีช่องค้นหาและเลือก favorite
   - ดึงข้อมูลจาก Bitkub API `/api/market/ticker`

2. หน้าแสดงรายละเอียดเหรียญ (Symbol Page)
   - แสดงชื่อเหรียญ, ราคา, เปอร์เซ็นต์เปลี่ยน, กราฟราคา
   - แสดง Order Book (Bids / Asks)
   - แสดง Recent Trades
   - ใช้ API:  
     - `/api/market/depth?symbol=XXX`
     - `/api/market/trades?symbol=XXX`

3. หน้าเทรด (Trade)
   - แบบฟอร์มซื้อ/ขายเหรียญ (Buy/Sell)
   - เลือกประเภทคำสั่ง: Limit / Market
   - ฟิลด์: ราคา, จำนวน, มูลค่ารวม
   - ปุ่มส่งคำสั่ง → backend → Bitkub API
   - ใช้ API (private):  
     - `POST /api/market/place-bid`
     - `POST /api/market/place-ask`
     - `POST /api/market/cancel-order`
     - `POST /api/market/open-orders`

4. หน้า Wallet / Portfolio
   - แสดงยอดเงินทั้งหมด (total balance)
   - แสดงเหรียญทั้งหมดในพอร์ต (coin, available, reserved, total)
   - แสดงมูลค่าเงินบาทรวม
   - ใช้ API (private): `POST /api/user/wallet`

5. หน้า Deposit / Withdraw
   - Deposit: แสดงที่อยู่ฝาก (QR code + address)  
     → API: `GET /api/v4/crypto/addresses?coin=XXX`
   - Withdraw: ฟอร์มใส่ address, amount, network, note  
     → API: `POST /api/v4/crypto/withdraws`
   - ประวัติการฝากถอน (table)
   - มีระบบยืนยัน 2FA ก่อนถอน (OTP modal จำลอง)

6. หน้า Order History
   - แสดงรายการคำสั่งซื้อขายทั้งหมด
   - ฟิลเตอร์ตาม symbol / status / date
   - API: `/api/market/order-history`

7. หน้า Admin (เฉพาะ backend)
   - แสดงผู้ใช้, API key ที่เชื่อมต่อ, log ของการเทรด
   - สรุปยอดรวมทุกพอร์ต
   - ระบบแจ้งเตือน error จาก Bitkub API (rate limit / invalid timestamp)

---

### ⚙️ Backend (Node.js / Express)
- มี service `bitkubClient.js` สำหรับจัดการการเรียก API ทั้งหมด
- ฟังก์ชันหลัก:
  - `getMarketTicker()`
  - `getDepth(symbol)`
  - `getTrades(symbol)`
  - `getWallet(apiKey, secret)`
  - `placeOrder(apiKey, secret, side, amount, price, symbol)`
  - `cancelOrder(apiKey, secret, orderId)`
  - `getDepositAddress(apiKey, secret, coin)`
  - `withdraw(apiKey, secret, coin, address, amount, network)`
- มีระบบ signature generator ตามเอกสาร Bitkub (`HMAC_SHA256`)
- เก็บ API key / secret ไว้ใน `.env` หรือ DB แบบเข้ารหัส (ห้ามฝังใน client)

---

### 🧩 ส่วนประกอบหน้าเว็บ (Frontend Components)
- Header: Logo, Search, Wallet summary, User dropdown
- MarketList: ตารางคู่เหรียญ (sortable + filter)
- ChartSection: กราฟราคา (ใช้ Recharts หรือ TradingView widget)
- OrderBook: 2 คอลัมน์ (Bids / Asks)
- TradeFeed: รายการเทรดล่าสุด
- TradeForm: Buy/Sell panel
- WalletCard: แสดงยอดแต่ละเหรียญ
- WithdrawModal: ฟอร์มถอนพร้อม OTP
- Notifications: Toast แสดงสถานะคำสั่ง

---

### 💾 Database Schema (MySQL / MongoDB ก็ได้)
1. users(user_id, email, password_hash, created_at)
2. api_keys(user_id, api_key, encrypted_secret)
3. wallets(user_id, coin, available, reserved, total)
4. orders(order_id, user_id, symbol, side, price, amount, status, created_at)
5. deposits(withdraw_id, user_id, coin, address, amount, status, created_at)
6. logs(id, type, message, created_at)

---

### 🔐 ระบบความปลอดภัย
- ห้ามเก็บ secret key ใน localStorage
- Backend ต้องเป็น proxy ทุกครั้งที่เรียก Bitkub API
- ใช้ timestamp sync จาก `/api/servertime`
- Rate limit ทุก request
- ป้องกัน double-submit (ใช้ order_id เดียวกันซ้ำไม่ได้)
- แจ้ง error code ของ Bitkub แบบเข้าใจง่าย เช่น “Insufficient balance”, “Invalid signature”

---

### 🧭 ฟีเจอร์เสริม (Optional)
- Theme Light / Dark
- Multi-language (ไทย/อังกฤษ)
- ระบบจำลองเทรด (Demo mode)
- Export order history เป็น CSV
- Notifications real-time (WebSocket)
- ใช้ Chart.js หรือ Recharts แสดงกราฟราคา

---

### 💬 สิ่งที่ต้องให้ AI ทำให้ครบ
1. สร้างโครงสร้างโปรเจกต์ทั้งหมด (frontend + backend)
2. เขียนโค้ดทุกหน้าที่ระบุด้านบน
3. ตั้งค่า `.env` สำหรับ Bitkub API key, secret
4. Mock data สำหรับ public endpoints ถ้าไม่มี API key
5. ทำ UI Responsive สวยงามในแนว dashboard เทรด
6. ใช้ Tailwind + shadcn/ui สำหรับ style ที่ดูทันสมัย
7. แสดงตัวอย่างข้อมูลจริงจาก Bitkub API (ใช้ public endpoints)

---

### 🧱 Output ที่ต้องการ
- เว็บระบบเทรดพร้อมหน้า Market, Trade, Wallet, Withdraw, History, Admin
- มี backend พร้อมเชื่อม API ของ Bitkub
- โครงสร้างไฟล์ชัดเจน เช่น  
```

/client  ← frontend React
/server  ← backend Node.js
.env

```
- พร้อมให้รันด้วยคำสั่ง  
```

npm install
npm run dev

```

---

ให้ AI เขียนโค้ดทั้งหมดในโปรเจกต์นี้ให้เสร็จใน prompt เดียว
```

---

อยากให้ผมปรับ prompt นี้ให้ตรงกับเครื่องมือที่คุณจะใช้ไหมครับ
(เช่น “Google Studio Code AI”, “v0.dev”, หรือ “ChatGPT โหมด Developer”)
เพราะแต่ละตัวมีรูปแบบรับ prompt ไม่เหมือนกัน — ผมจะจัดให้เข้ากับระบบนั้นได้เลย.

