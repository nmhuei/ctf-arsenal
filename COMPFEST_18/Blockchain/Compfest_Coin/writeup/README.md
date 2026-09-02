# Writeup: Compfest Coin

| Property | Value |
| :--- | :--- |
| **Category** | `Blockchain` |
| **Points** | `100` |
| **Author** | `-` |
| **Solves** | `31` |

---

## 📝 Challenge Overview

```
ALL IN, HIGH-RISK, HIGH-REWARD.

Starter tooling:
- https://docs.sui.io/guides/developer/getting-started
- @mysten/sui TypeScript SDK

Sui CLI cannot be used to interact.
```

Challenge Move modules:
- `assets.move`: Định nghĩa các coin marker structs `SUIX`, `USDC`, `CFX` có `drop`.
- `config.move`: Cấu hình phí và mục tiêu `min_effective_liquidity = 500`, `bounty_target = 500`.
- `registry.move`: Quản lý danh sách các thị trường (markets) và chiến lược (strategies).
- `pool.move`: Quản lý các RoutePool và tính toán `quoted_route_score`.
- `vault.move`: Quản lý IncentiveVault và giải ngân phần thưởng `claim_route_incentives`.
- `setup.move`: Kiểm tra điều kiện giải quyết `is_qualified(account, config)` (yêu cầu `earned >= bounty_target = 500`).

---

## 🔍 Phân tích & Lỗ hổng (Vulnerability Analysis)

### 1. Phân tích `vault::claim_route_incentives`
```move
public entry fun claim_route_incentives<Base, Quote, Strategy>(
    vault: &mut IncentiveVault<CFX>,
    pool: &mut RoutePool<Base, Quote>,
    strategy: &RouteStrategy<Strategy>,
    position: &RoutePosition<Base, Quote>,
    account: &mut OperatorAccount<CFX>,
    oracle: &PriceOracle,
    config: &GlobalConfig,
    ctx: &TxContext,
) {
    let operator = tx_context::sender(ctx);
    assert!(!table::contains(&vault.claimed, operator), EAlreadyClaimed);
    assert!(math::same_bytes(&vault.market, &pool::canonical_market(pool)), EWrongMarket);
    assert!(math::same_bytes(&vault.market, registry::market(strategy)), EStrategyNotRegistered);
    assert!(pool::position_pool(position) == object::id(pool), 9);
    assert!(pool::effective_liquidity(pool, position) >= config::min_effective_liquidity(config), EInsufficientCfx);

    let claim = pool::quoted_route_score(pool, oracle);
    let amount = math::min(claim, vault.balance);
    vault.balance = vault.balance - amount;
    account.earned = account.earned + amount;
    table::add(&mut vault.claimed, operator, true);
    event::emit(IncentivesClaimed { operator, amount });
}
```

* **Điều kiện 1**: `vault.market` là `canonical_market<SUIX, USDC>()`.
  * Hàm `canonical_market<A, B>()` sắp xếp tên 2 kiểu dữ liệu theo thứ tự alphabet.
  * Do đó, cả `canonical_market<SUIX, USDC>()` và `canonical_market<USDC, SUIX>()` đều trả về cùng một chuỗi canonical market!
* **Điều kiện 2**: Tính điểm thưởng `pool::quoted_route_score`:
  ```move
  public fun quoted_route_score<Base, Quote>(
      pool: &RoutePool<Base, Quote>,
      oracle: &PriceOracle,
  ): u64 {
      let raw = pool.reserve_quote / pool.reserve_base;
      let oracle_price = oracle::price_e6(oracle);
      if (raw > oracle_price) { raw } else { oracle_price }
  }
  ```
  * Điểm thưởng tính theo tỉ lệ `raw = pool.reserve_quote / pool.reserve_base`.
  * Trong pool mặc định do `setup` khởi tạo (`<SUIX, USDC>`), `reserve_base = 1_000_000, reserve_quote = 1_000_000` ➔ `raw = 1` (không đủ 500 điểm để pass `is_qualified`).

### 2. Khởi tạo Custom RoutePool với tỉ lệ dự trữ mất cân bằng
* Hàm `pool::create_route_pool<Base, Quote>` cho phép bất kỳ ai tạo thêm pool mới:
  ```move
  let direct = registry::direct_market<Base, Quote>();
  assert!(!registry::has_market(registry, &direct), EMarketAlreadyRegistered);
  ```
* Trong `registry`, thị trường đã đăng ký ban đầu là `direct_market<SUIX, USDC>()` (tức `SUIX|USDC`).
* Thị trường đảo ngược `direct_market<USDC, SUIX>()` (tức `USDC|SUIX`) **chưa từng được đăng ký** trong `registry`!
* Do đó, ta hoàn toàn có thể gọi:
  ```move
  pool::create_route_pool<USDC, SUIX>(registry, config, reserve_base = 1, reserve_quote = 1_000_000, ctx);
  ```
  * Pool mới này có `canonical_market` trùng khớp hoàn toàn với `vault.market`.
  * Tỉ lệ dự trữ: `reserve_base = 1` (USDC) và `reserve_quote = 1_000_000` (SUIX).
  * Điểm thưởng: `raw = 1_000_000 / 1 = 1_000_000`!

### 3. Kịch bản khai thác hoàn chỉnh (Exploit Sequence)
1. **Đăng ký Strategy**: Gọi `registry::register_route_strategy<SUIX, USDC, SUIX>(registry, SUIX{}, ctx)`.
2. **Tạo Pool mới**: Gọi `pool::create_route_pool<USDC, SUIX>(registry, config, 1, 1_000_000, ctx)`.
3. **Mở Position**: Gọi `pool::open_position<USDC, SUIX>(new_pool, ctx)`.
4. **Cung cấp thanh khoản**: Gọi `pool::add_liquidity<USDC, SUIX>(new_pool, position, 1000, config)` để đạt `effective_liquidity = 1000 >= 500`.
5. **Nhận thưởng Incentive**: Gọi `vault::claim_route_incentives<USDC, SUIX, SUIX>(vault, new_pool, strategy, position, operator_account, oracle, config, ctx)`.
   * Nhận `min(1_000_000, 1000) = 1000` CFX vào `account.earned`.
6. **Solve**: Gọi `setup::solve(setup, operator_account, config)`.
   * `is_qualified` kiểm tra `account.earned = 1000 >= 500` ➔ `setup.solved = true`.

---

## 💻 Script khai thác

Script TypeScript/Node.js khai thác tương tác qua `@mysten/sui` SDK tại [`../solver/solve.mjs`](../solver/solve.mjs).
