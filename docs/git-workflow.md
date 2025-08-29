# Git 分支策略

## 分支结构

```
main (生产分支)
├── develop (开发主分支)
│   ├── feature/shopify-inventory-api (功能分支)
│   ├── feature/shopify-recommendation-api (功能分支)
│   └── feature/weather-enhancements (功能分支)
├── hotfix/critical-bug-fix (热修复分支)
└── release/v1.0.0 (发布分支)
```

## 分支说明

### 🚀 main (生产分支)
- **用途**: 生产环境代码，始终保持稳定
- **保护**: 只能通过 PR 合并，需要代码审查
- **标签**: 每次发布打 tag (v1.0.0, v1.1.0...)

### 🔧 develop (开发主分支)
- **用途**: 集成所有功能开发，日常开发基础分支
- **来源**: 从 main 创建
- **合并**: 功能分支合并到此分支

### ✨ feature/* (功能分支)
- **命名**: `feature/功能描述`
- **用途**: 开发新功能
- **来源**: 从 develop 创建
- **合并**: 完成后合并回 develop

### 🐛 hotfix/* (热修复分支)
- **命名**: `hotfix/问题描述`
- **用途**: 紧急修复生产问题
- **来源**: 从 main 创建
- **合并**: 同时合并到 main 和 develop

### 🎯 release/* (发布分支)
- **命名**: `release/v版本号`
- **用途**: 准备发布，最后的测试和修复
- **来源**: 从 develop 创建
- **合并**: 完成后合并到 main 和 develop

## 工作流程

### 开发新功能
```bash
# 1. 切换到 develop 并更新
git checkout develop
git pull origin develop

# 2. 创建功能分支
git checkout -b feature/shopify-inventory-api

# 3. 开发和提交
git add .
git commit -m "feat: 添加库存查询 API 功能"

# 4. 推送分支
git push -u origin feature/shopify-inventory-api

# 5. 创建 PR 到 develop
```

### 发布流程
```bash
# 1. 创建发布分支
git checkout develop
git checkout -b release/v1.0.0

# 2. 最后的测试和修复
git commit -m "chore: 准备 v1.0.0 发布"

# 3. 合并到 main
git checkout main
git merge release/v1.0.0
git tag v1.0.0
git push origin main --tags

# 4. 合并回 develop
git checkout develop
git merge release/v1.0.0
```

### 热修复流程
```bash
# 1. 从 main 创建热修复分支
git checkout main
git checkout -b hotfix/critical-security-fix

# 2. 修复问题
git commit -m "fix: 修复安全漏洞"

# 3. 合并到 main
git checkout main
git merge hotfix/critical-security-fix
git tag v1.0.1

# 4. 合并到 develop
git checkout develop
git merge hotfix/critical-security-fix
```

## 提交信息规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

- `feat:` 新功能
- `fix:` 修复 bug
- `docs:` 文档更新
- `style:` 代码格式调整
- `refactor:` 重构代码
- `test:` 添加或修改测试
- `chore:` 构建过程或辅助工具的变动

## 分支保护规则

### main 分支
- 禁止直接推送
- 需要 PR 审查
- 需要通过 CI 检查
- 需要最新的 develop 分支

### develop 分支
- 需要 PR 审查
- 需要通过 CI 检查

## 建议的功能分支

基于当前项目，建议创建以下功能分支：

1. `feature/shopify-inventory-integration` - 库存系统集成
2. `feature/shopify-recommendation-engine` - 推荐引擎
3. `feature/external-api-rate-limiting` - API 限流功能
4. `feature/caching-system` - 缓存系统优化
5. `feature/monitoring-logging` - 监控和日志
6. `feature/api-documentation` - API 文档
