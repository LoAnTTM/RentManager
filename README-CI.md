# 🚀 CI/CD Local Testing Guide

Chạy kiểm tra CI/CD trước khi push lên GitHub để tránh lỗi!

## 📋 Các cách chạy CI checks

### 1. **Sử dụng Makefile (Khuyến nghị)**

```bash
# Chạy tất cả CI checks (giống GitHub Actions)
make ci-check

# Quick check (bỏ qua Docker build, nhanh hơn)
make ci-quick
```

### 2. **Sử dụng Script trực tiếp**

```bash
# Full CI check
./scripts/ci-check.sh

# Quick check
make ci-quick
```

### 3. **Git Pre-push Hook (Tự động)**

Setup hook để tự động chạy checks trước mỗi lần push:

```bash
# Setup hooks
chmod +x scripts/setup-git-hooks.sh
./scripts/setup-git-hooks.sh
```

Sau khi setup, mỗi lần `git push` sẽ tự động chạy CI checks. Nếu fail, push sẽ bị chặn.

**Skip hooks (không khuyến nghị):**
```bash
git push --no-verify
```

### 4. **Chạy GitHub Actions locally với `act`**

Cài đặt `act`:
```bash
# macOS
brew install act

# Linux
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash
```

Chạy:
```bash
# Chạy CI workflow
make ci-act

# Hoặc chạy workflow cụ thể
act -W .github/workflows/ci.yml push
```

## 🔍 CI Checks bao gồm

### Backend
- ✅ **flake8** - Lint Python code
- ✅ **black** - Check code formatting
- ✅ **isort** - Check import sorting
- ✅ **mypy** - Type checking (non-blocking)
- ✅ **pytest** - Run tests

### Frontend
- ✅ **TypeScript** - Type checking (`tsc --noEmit`)
- ✅ **ESLint** - Lint JavaScript/TypeScript
- ✅ **Build** - Test Next.js build

### Docker
- ✅ **Backend image** - Build test
- ✅ **Frontend image** - Build test

## 🛠️ Fix lỗi thường gặp

### Backend venv không tồn tại
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install pytest flake8 black isort mypy
```

### Frontend dependencies
```bash
cd webAdmin
npm ci
```

### Docker không chạy được
- Bỏ qua Docker checks: `make ci-quick`
- Hoặc cài Docker Desktop

## 📝 Workflow

**Trước khi push:**
```bash
# 1. Chạy CI checks
make ci-check

# 2. Nếu pass, push
git push

# 3. Nếu fail, fix lỗi rồi chạy lại
```

**Với pre-push hook:**
```bash
# Chỉ cần push, hook sẽ tự động chạy checks
git push
```

## ⚡ Tips

1. **Quick check thường xuyên:**
   ```bash
   make ci-quick  # Nhanh hơn, bỏ qua Docker
   ```

2. **Fix formatting tự động:**
   ```bash
   make format-backend  # Auto-fix Python formatting
   ```

3. **Chạy từng phần:**
   ```bash
   make lint-backend    # Chỉ lint backend
   make lint-frontend   # Chỉ lint frontend
   make test-backend    # Chỉ test backend
   ```

4. **CI checks trong Docker:**
   ```bash
   # Nếu đã có Docker running
   make test            # Chạy tests trong container
   ```

## 🎯 Best Practices

1. ✅ Chạy `make ci-check` trước khi commit
2. ✅ Setup pre-push hook để tự động check
3. ✅ Fix lỗi linting ngay khi phát hiện
4. ✅ Chạy tests trước khi push
5. ✅ Đảm bảo build thành công

## 🔗 Tài liệu thêm

- [Git Hooks](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks)
- [act - Run GitHub Actions locally](https://github.com/nektos/act)
- [GitHub Actions](https://docs.github.com/en/actions)

