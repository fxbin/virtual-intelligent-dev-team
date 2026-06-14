# 端到端示例：从小切片到发布门禁的完整流程

这个示例展示了如何使用 Virtual Intelligent Dev Team 完成一个完整的功能开发流程，从最初的小切片交付到最终的发布门禁检查。

---

## 场景背景

**用户需求：**
为一个 Spring Boot 应用添加用户登录功能，包括邮箱+密码认证、JWT Token 生成、Token 验证中间件。

**复杂度：**
- 涉及多个模块（Controller、Service、Repository、Security Config）
- 需要数据库迁移（users 表）
- 需要集成测试
- 属于安全敏感变更

---

## 阶段 1：意图确认与路由

### 用户输入

```bash
/virtual-intelligent-dev-team 我想添加用户登录功能
```

### 系统响应：意图确认

由于这是一个模糊请求，系统会先进行意图确认：

```markdown
# 意图确认

你的请求"添加用户登录功能"可以从多个角度切入：

**请选择你的主要目标：**

1. **product-opportunity**（产品机会验证）
   - 适用场景：你还在验证是否需要这个功能
   - 会做什么：分析用户需求、竞品调研、产品定义
   - Lead Agent: World-Class Product Architect

2. **prototype-exploration**（原型探索）
   - 适用场景：你需要先做一个可交互的原型
   - 会做什么：设计 UI、制作 HTML 原型、用户流程
   - Lead Agent: World-Class Product Architect → Prototype Design Council

3. **technical-feasibility**（技术可行性评估）
   - 适用场景：你不确定技术方案是否可行
   - 会做什么：评估认证方案、安全性分析、技术选型
   - Lead Agent: Technical Trinity

4. **architecture-risk**（架构风险分析）
   - 适用场景：这是一个高风险变更，需要治理
   - 会做什么：风险评估、架构影响分析、回滚方案
   - Lead Agent: Sentinel Architect

5. **delivery-plan**（交付拆解）
   - 适用场景：你已经明确要做，需要拆解成可执行的任务
   - 会做什么：拆解任务、制定计划、确定里程碑
   - Lead Agent: Technical Trinity → Quick Slice Delivery

**你的选择是？**
```

### 用户选择

```bash
5. delivery-plan
```

---

## 阶段 2：Quick Slice Delivery（小切片交付）

系统路由到 **Technical Trinity** → **Quick Slice Delivery Playbook**

### Step 2.1: 生成 Quick Slice Brief

```yaml
---
task_id: auth-login-20260614-001
workflow: quick-slice-delivery
lead_agent: Technical Trinity
---

# Quick Slice Brief: 用户登录功能

## 目标（Goal）
为 Spring Boot 应用添加邮箱+密码登录功能，使用 JWT Token 进行认证。

## 范围（Scope）

**包含：**
- 用户注册接口（POST /api/auth/register）
- 用户登录接口（POST /api/auth/login）
- JWT Token 生成逻辑
- Token 验证中间件
- users 表数据库迁移
- 单元测试 + 集成测试

**不包含：**
- 密码重置功能
- 第三方登录（OAuth）
- 用户角色权限管理
- 前端页面

## 验收条件（Acceptance Criteria）

1. 用户可以通过 POST /api/auth/register 注册账号
2. 用户可以通过 POST /api/auth/login 登录并获得 JWT Token
3. Token 可以通过 Authorization Header 验证
4. 密码必须经过 BCrypt 加密存储
5. 所有测试通过（单元测试 + 集成测试）
6. 数据库迁移成功（users 表创建）

## 技术约束（Technical Constraints）

- Spring Boot 3.2+
- Spring Security 6.x
- PostgreSQL 15+
- JWT Library: jjwt 0.12.x
- 密码加密：BCrypt

## 风险与依赖（Risks & Dependencies）

**风险：**
- 安全敏感变更：密码存储、Token 生成必须符合安全最佳实践
- 数据库迁移：需要在生产环境谨慎执行

**依赖：**
- 需要 jjwt 依赖（添加到 pom.xml）
- 需要 Spring Security 配置

## 下一步（Next Steps）

1. 实现代码
2. 运行测试
3. 提交 Delivery Status
4. 进入 Release Gate 检查
```

### Step 2.2: 实现代码

系统开始实现代码（省略具体代码细节，假设已实现以下文件）：

```
src/main/java/com/example/
  ├── controller/AuthController.java
  ├── service/AuthService.java
  ├── service/JwtService.java
  ├── repository/UserRepository.java
  ├── model/User.java
  ├── dto/RegisterRequest.java
  ├── dto/LoginRequest.java
  ├── dto/AuthResponse.java
  ├── security/JwtAuthenticationFilter.java
  └── security/SecurityConfig.java

src/main/resources/db/migration/
  └── V001__create_users_table.sql

src/test/java/com/example/
  ├── controller/AuthControllerTest.java
  ├── service/AuthServiceTest.java
  └── integration/AuthIntegrationTest.java
```

### Step 2.3: 运行测试

```bash
mvn test
```

**测试结果：**
```
[INFO] Tests run: 15, Failures: 0, Errors: 0, Skipped: 0
[INFO] BUILD SUCCESS
```

### Step 2.4: 生成 Delivery Status

```yaml
---
task_id: auth-login-20260614-001
status: implemented
timestamp: 2026-06-14T10:30:00Z
---

# Delivery Status: 用户登录功能

## 已完成（Completed）

✅ 用户注册接口（POST /api/auth/register）
✅ 用户登录接口（POST /api/auth/login）
✅ JWT Token 生成逻辑（JwtService）
✅ Token 验证中间件（JwtAuthenticationFilter）
✅ users 表数据库迁移（V001__create_users_table.sql）
✅ 单元测试（15 个测试通过）
✅ 集成测试（3 个端到端测试通过）

## 验证证据（Verification Evidence）

### 1. 功能验证
- 命令：`curl -X POST http://localhost:8080/api/auth/register -d '{"email":"test@example.com","password":"Test123!"}'`
- 结果：用户注册成功，返回 201 Created

- 命令：`curl -X POST http://localhost:8080/api/auth/login -d '{"email":"test@example.com","password":"Test123!"}'`
- 结果：登录成功，返回 JWT Token

### 2. 测试验证
- 命令：`mvn test`
- 结果：15 tests passed, 0 failures

### 3. 安全验证
- 密码存储：使用 BCrypt 加密（已验证）
- Token 签名：使用 HS256 算法（已验证）
- Token 过期：24 小时后过期（已验证）

## 未覆盖范围（Uncovered Scope）

❌ 密码重置功能（不在此次范围）
❌ 第三方登录（不在此次范围）
❌ 用户角色权限管理（后续迭代）
❌ 前端页面（不在此次范围）

## 残留风险（Residual Risk）

- **中风险**：数据库迁移在生产环境执行时需要人工确认
- **低风险**：JWT Secret 需要在生产环境通过环境变量配置

## 信心等级（Confidence Grade）

**HIGH**（高信心）

理由：
- 所有测试通过
- 安全最佳实践已遵循
- 代码经过本地验证

## 下一步建议（Next Steps）

1. 进入 Release Gate 检查
2. 人工审查安全配置
3. 准备生产环境部署
```

---

## 阶段 3：Release Gate（发布门禁）

### Step 3.1: 激活 Release Gate Playbook

用户确认进入发布门禁：

```bash
/virtual-intelligent-dev-team 进入 release gate 检查
```

### Step 3.2: 完成证据检查

系统读取 `Delivery Status` 并进行完成证据门禁检查：

```yaml
---
gate_id: release-gate-auth-login-20260614-001
gate_type: release-gate
task_id: auth-login-20260614-001
timestamp: 2026-06-14T10:45:00Z
---

# Release Gate Result: 用户登录功能

## 完成证据评估（Completion Evidence Assessment）

### 1. Action（行动）
✅ **PASS**
- 已实现 7 个核心模块
- 已添加 15 个测试
- 已创建数据库迁移脚本

### 2. Result（结果）
✅ **PASS**
- 所有测试通过（15/15）
- 功能验证通过（注册、登录、Token 验证）
- 安全验证通过（BCrypt 加密、JWT 签名）

### 3. Covered Scope（覆盖范围）
✅ **PASS**
- 用户注册 ✅
- 用户登录 ✅
- JWT Token 生成 ✅
- Token 验证中间件 ✅
- 数据库迁移 ✅
- 测试覆盖 ✅

### 4. Uncovered Scope（未覆盖范围）
✅ **PASS**
- 明确声明不在范围内的功能（密码重置、OAuth、前端）
- 无遗漏的必须功能

### 5. Residual Risk（残留风险）
⚠️ **HOLD**
- **中风险**：数据库迁移在生产环境执行时需要人工确认
- **低风险**：JWT Secret 需要在生产环境通过环境变量配置

**建议：** 需要人工审查数据库迁移计划

### 6. Confidence Grade（信心等级）
✅ **PASS**
- HIGH 信心等级合理
- 有充分的验证证据支持

### 7. Evidence Refs（证据引用）
✅ **PASS**
- 提供了可验证的 curl 命令
- 提供了测试命令（mvn test）
- 证据新鲜且可重现

## Ship/Hold 决策（Ship/Hold Decision）

**决策：HOLD**（暂缓发布）

**理由：**
1. 完成证据充分（6/7 PASS）
2. 但存在中风险：生产数据库迁移需要人工确认
3. 需要补充：生产环境部署计划

**需要补充的内容：**
1. 生产数据库迁移计划（包含回滚方案）
2. JWT Secret 的生产环境配置指南
3. 监控和日志配置

## 补救建议（Remediation Brief）

### Priority Tasks（优先任务）

1. **创建数据库迁移计划**
   - 内容：V001__create_users_table.sql 的生产执行步骤
   - 回滚方案：DROP TABLE users 的脚本
   - 预计时间：30 分钟

2. **创建生产环境配置指南**
   - 内容：JWT_SECRET 环境变量配置说明
   - 示例：如何生成安全的 Secret
   - 预计时间：15 分钟

3. **添加监控和日志**
   - 登录失败次数监控
   - Token 验证失败日志
   - 预计时间：1 小时

### 完成后重新进入 Release Gate

完成以上补救任务后，重新提交 `Delivery Status` 并进入 Release Gate 检查。
```

---

## 阶段 4：补救与重新检查

### Step 4.1: 补救任务

系统根据 Remediation Brief 执行补救任务：

**1. 创建数据库迁移计划**

```markdown
# 生产数据库迁移计划

## 执行步骤

1. **备份当前数据库**
   ```bash
   pg_dump -U postgres -d production_db > backup_20260614.sql
   ```

2. **执行迁移**
   ```bash
   mvn flyway:migrate -Dflyway.url=jdbc:postgresql://prod-db:5432/production_db
   ```

3. **验证迁移**
   ```bash
   psql -U postgres -d production_db -c "\d users"
   ```

## 回滚方案

如果迁移失败，执行以下回滚：

```sql
DROP TABLE IF EXISTS users CASCADE;
```

然后恢复备份：

```bash
psql -U postgres -d production_db < backup_20260614.sql
```

## 预计执行时间

- 备份：5 分钟
- 迁移：2 分钟
- 验证：1 分钟
- 总计：8 分钟
```

**2. 创建生产环境配置指南**

```markdown
# 生产环境配置指南

## JWT Secret 配置

### 1. 生成安全的 Secret

```bash
openssl rand -base64 64
```

### 2. 配置环境变量

在生产服务器上配置：

```bash
export JWT_SECRET="<生成的 Secret>"
export JWT_EXPIRATION=86400000  # 24 小时
```

### 3. 验证配置

启动应用后，检查日志：

```bash
tail -f /var/log/app.log | grep "JWT Secret loaded"
```

## 安全注意事项

- JWT Secret 必须至少 256 位
- 不要将 Secret 提交到代码仓库
- 定期轮换 Secret（建议每 3 个月）
```

**3. 添加监控和日志**

```java
// AuthService.java 中添加日志和监控
@Service
public class AuthService {
    
    private final UserRepository userRepository;
    private final JwtService jwtService;
    private final Logger logger = LoggerFactory.getLogger(AuthService.class);
    
    public AuthResponse login(LoginRequest request) {
        try {
            User user = userRepository.findByEmail(request.getEmail())
                .orElseThrow(() -> {
                    logger.warn("Login failed: user not found - {}", request.getEmail());
                    return new InvalidCredentialsException();
                });
            
            if (!passwordEncoder.matches(request.getPassword(), user.getPassword())) {
                logger.warn("Login failed: invalid password - {}", request.getEmail());
                throw new InvalidCredentialsException();
            }
            
            String token = jwtService.generateToken(user);
            logger.info("Login successful - {}", request.getEmail());
            
            return new AuthResponse(token);
        } catch (Exception e) {
            logger.error("Login error - {}: {}", request.getEmail(), e.getMessage());
            throw e;
        }
    }
}
```

### Step 4.2: 更新 Delivery Status

补救完成后，更新 `Delivery Status`：

```yaml
---
task_id: auth-login-20260614-001
status: remediation-completed
timestamp: 2026-06-14T12:00:00Z
---

# Delivery Status: 用户登录功能（补救完成）

## 新增完成项（New Completions）

✅ 生产数据库迁移计划（包含回滚方案）
✅ 生产环境配置指南（JWT Secret）
✅ 监控和日志（登录失败、Token 验证失败）

## 补救证据（Remediation Evidence）

1. **数据库迁移计划**
   - 文件：`docs/production-migration-plan.md`
   - 包含：备份、迁移、验证、回滚步骤

2. **配置指南**
   - 文件：`docs/production-config-guide.md`
   - 包含：Secret 生成、环境变量配置、验证步骤

3. **监控和日志**
   - 代码：`src/main/java/com/example/service/AuthService.java`
   - 日志级别：INFO（成功）、WARN（失败）、ERROR（异常）

## 残留风险更新（Updated Residual Risk）

- ~~中风险：数据库迁移在生产环境执行时需要人工确认~~ → **已缓解**（有详细计划和回滚方案）
- ~~低风险：JWT Secret 需要在生产环境通过环境变量配置~~ → **已缓解**（有配置指南）

## 信心等级（Confidence Grade）

**HIGH**（高信心）→ **VERY HIGH**（极高信心）

理由：
- 所有风险已缓解
- 补充了生产环境部署文档
- 添加了监控和日志

## 准备就绪（Ready for Release Gate Re-check）

✅ 所有补救任务已完成
✅ 残留风险已缓解
✅ 生产环境部署准备就绪
```

### Step 4.3: 重新进入 Release Gate

```yaml
---
gate_id: release-gate-auth-login-20260614-002
gate_type: release-gate
task_id: auth-login-20260614-001
timestamp: 2026-06-14T12:15:00Z
---

# Release Gate Result: 用户登录功能（重新检查）

## 完成证据评估（Completion Evidence Assessment）

### 1. Action（行动）
✅ **PASS**

### 2. Result（结果）
✅ **PASS**

### 3. Covered Scope（覆盖范围）
✅ **PASS**

### 4. Uncovered Scope（未覆盖范围）
✅ **PASS**

### 5. Residual Risk（残留风险）
✅ **PASS**
- 所有风险已缓解
- 有详细的生产部署计划

### 6. Confidence Grade（信心等级）
✅ **PASS**
- VERY HIGH 信心等级合理

### 7. Evidence Refs（证据引用）
✅ **PASS**
- 补充了生产环境文档
- 证据完整且可验证

## Ship/Hold 决策（Ship/Hold Decision）

**决策：SHIP**（批准发布）

**理由：**
1. 完成证据充分（7/7 PASS）
2. 所有风险已缓解
3. 生产环境准备就绪

**发布清单：**
- [x] 代码已合并到 main 分支
- [x] 数据库迁移计划已准备
- [x] 生产环境配置指南已准备
- [x] 监控和日志已添加
- [x] 测试通过（15/15）
- [x] 代码审查已完成

## 下一步（Next Steps）

1. 在生产环境执行数据库迁移
2. 配置 JWT Secret 环境变量
3. 部署新版本
4. 监控登录功能运行状况
5. 进入 Post-Release Feedback Loop
```

---

## 阶段 5：Post-Release Feedback Loop（发布后反馈）

### Step 5.1: 监控发布后运行状况

发布 7 天后，系统自动生成反馈报告：

```yaml
---
feedback_id: post-release-auth-login-20260614-001
task_id: auth-login-20260614-001
timestamp: 2026-06-21T10:00:00Z
---

# Post-Release Feedback: 用户登录功能

## 运行状况（Operational Health）

### 1. 功能指标

- **总登录次数**：12,450
- **成功登录**：12,180（97.8%）
- **失败登录**：270（2.2%）
- **平均响应时间**：85ms
- **P95 响应时间**：150ms
- **P99 响应时间**：320ms

### 2. 错误分析

**主要错误类型：**
1. 无效密码（180 次，66.7%）
2. 用户不存在（60 次，22.2%）
3. Token 验证失败（30 次，11.1%）

**异常情况：**
- 无严重错误
- 无性能问题
- 无安全漏洞报告

### 3. 用户反馈

**正面反馈：**
- 登录速度快
- Token 过期时间合理

**负面反馈：**
- 用户希望支持"记住我"功能（3 个反馈）
- 用户希望支持第三方登录（2 个反馈）

## 改进建议（Improvement Recommendations）

### 优先级 1（高优先级）
无

### 优先级 2（中优先级）
1. **添加"记住我"功能**
   - 理由：用户有需求（3 个反馈）
   - 预计工作量：1 天
   - 建议时间：下一个迭代

### 优先级 3（低优先级）
1. **添加第三方登录**
   - 理由：用户有需求（2 个反馈）
   - 预计工作量：3 天
   - 建议时间：未来规划

## 根因分析（Root Cause Analysis）

**登录失败原因：**
- 66.7% 是用户输入错误密码（正常行为）
- 22.2% 是用户输入不存在的邮箱（正常行为）
- 11.1% 是 Token 验证失败（需要调查）

**Token 验证失败调查：**
- 原因：客户端未正确传递 Authorization Header
- 解决方案：更新客户端文档，说明正确的 Header 格式

## 下一步行动（Next Actions）

1. 更新客户端文档（Authorization Header 格式）
2. 将"记住我"功能加入下一个迭代的 backlog
3. 将第三方登录功能加入未来规划
4. 继续监控 7 天
```

---

## 总结

### 完整流程回顾

1. **意图确认**：用户提出模糊需求 → 系统确认切入方向 → 选择 `delivery-plan`
2. **Quick Slice Delivery**：生成 Quick Slice Brief → 实现代码 → 运行测试 → 生成 Delivery Status
3. **Release Gate**：检查完成证据 → 发现残留风险 → 决策 HOLD → 提供补救建议
4. **补救与重新检查**：执行补救任务 → 更新 Delivery Status → 重新检查 → 决策 SHIP
5. **Post-Release Feedback**：监控运行状况 → 分析用户反馈 → 提供改进建议

### 关键机制

- ✅ **Worker-Verifier 分离**：Technical Trinity（Worker）实现代码，Release Gate（Verifier）验证完成证据
- ✅ **完成证据门禁**：7 个维度（Action、Result、Covered Scope、Uncovered Scope、Residual Risk、Confidence Grade、Evidence Refs）
- ✅ **Ship/Hold 决策**：基于完成证据做出 SHIP 或 HOLD 决策
- ✅ **Remediation Patch**：HOLD 时提供优先任务和建议
- ✅ **Post-Release Feedback Loop**：发布后持续监控并提供改进建议

### 使用的文档和 Schema

**Playbooks：**
- `quick-slice-delivery-playbook.md`
- `release-gate-playbook.md`
- `post-release-feedback-playbook.md`

**Schemas：**
- `completion-evidence.schema.json`
- `release-gate-result.schema.json`
- `delivery-cycle-report.schema.json`

**Templates：**
- `quick-slice-brief.md`
- `delivery-status.md`
- `remediation-brief-template.md`

---

## 如何复用这个流程

### 场景 1：小功能开发

使用 Quick Slice Delivery → Release Gate 即可，跳过 Post-Release Feedback（除非是关键功能）。

### 场景 2：大重构

使用 Pre-Development Planning Playbook → Bounded Iteration → Release Gate → Post-Release Feedback。

### 场景 3：高风险变更

路由到 Sentinel Architect → Architecture Risk Analysis → Release Gate（增强版，包含安全审查）。

### 场景 4：产品功能

路由到 World-Class Product Architect → Product Discovery Council → Prototype Design Council → Quick Slice Delivery → Release Gate。

---

**这就是一个完整的从小切片到发布门禁的端到端流程！**
