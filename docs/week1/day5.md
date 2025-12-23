# Day 5: 实现 `/posts` 创建接口并联调前端保存按钮

## 目标
- ✅ 完善后端 POST `/api/posts` 创建接口
- ✅ 创建前端保存文章页面和表单组件
- ✅ 实现前端与后端 API 联调
- ✅ 添加错误处理和成功提示
- ✅ 修复文章详情页日期显示问题
- ✅ 添加创建文章按钮到导航菜单
- ✅ 支持国际化（多语言）
- ✅ 实现文章详情页从后端 API 获取数据并显示

## 实现内容

### 1. 后端改进 (`backend/app/main.py`)

#### 1.1 添加依赖
- 引入 `logging` 用于日志记录
- `httpx` 已注释（Day 11 启用 n8n webhook 时需要）

#### 1.2 改进 POST `/api/posts` 接口
- 添加文档字符串说明
- 将文章保存到 PostgreSQL 数据库
- 返回格式化的响应数据
- 记录创建成功的日志
- **注意**: n8n webhook 调用代码已注释，等 Day 11 再启用

#### 1.3 数据模型
- `PostCreate`: 请求数据模型
  - `title`: 文章标题（必填）
  - `content`: 文章内容（必填）
  - `tags`: 标签列表（可选）
  - `slug`: URL slug（可选，不提供会自动生成）

#### 1.4 响应格式
- 使用 `format_post_response()` 函数统一格式化响应
- 包含文章 ID、标题、slug、内容、摘要、标签、创建时间等信息

### 2. 前端实现

#### 2.1 创建文章页面 (`NotionNext/pages/create-post.js`)

**功能特性:**
- ✅ 标题输入（必填）
- ✅ URL Slug 输入（可选，支持自动生成）
- ✅ 内容文本域（必填）
- ✅ 标签输入（逗号分隔）
- ✅ 自动生成 Slug: 基于标题自动生成 URL-friendly slug
- ✅ 表单验证: 必填字段验证
- ✅ 加载状态: 提交时显示加载状态
- ✅ 错误处理: 显示 API 错误信息
- ✅ 成功提示: 显示创建成功信息，3秒后自动跳转到文章详情页
- ✅ 响应式设计: 支持深色模式

**API 集成:**
- 调用 `POST /api/posts` 接口
- 处理响应和错误
- 成功后跳转到文章详情页（`/en/article/{slug}`）

#### 2.2 导航菜单集成 (`NotionNext/themes/simple/components/MenuList.js`)

**添加创建文章按钮:**
- ✅ 在导航菜单中添加"创建文章"按钮
- ✅ 使用国际化键 `locale.NAV.CREATE_POST`
- ✅ 图标: `fas fa-plus-circle`
- ✅ 链接: `/create-post`
- ✅ 始终显示（不受配置控制）
- ✅ 即使启用了自定义菜单，也会确保按钮显示

#### 2.3 国际化支持

**添加的语言文件:**
- `lib/lang/en-US.js`: "Create Post"
- `lib/lang/zh-CN.js`: "创建文章"
- `lib/lang/zh-TW.js`: "建立文章"
- `lib/lang/zh-HK.js`: "建立文章"
- `lib/lang/ja-JP.js`: "記事を作成"
- `lib/lang/fr-FR.js`: "Créer un article"
- `lib/lang/tr-TR.js`: "Gönderi Oluştur"

#### 2.4 文章详情页改进

**修复的问题:**
- ✅ 修复 `publishDay` 和 `lastEditedDay` 显示为空的问题
- ✅ 添加日期格式化函数，支持中英文格式
- ✅ 从后端 API 获取文章数据并转换为 Notion 兼容格式
- ✅ 支持通过 `/en/article/{slug}` 访问后端创建的文章

**实现文件:**
- `pages/[prefix]/[slug]/[...suffix].js`: 三级及以上路径路由
- `pages/[prefix]/[slug]/index.js`: 二级路径路由

**数据转换:**
- 将后端返回的纯文本内容转换为 Notion blockMap 格式
- 按段落分割内容，创建文本块
- 确保 blockMap 结构符合 NotionPage 组件要求

## 使用方式

### 1. 启动后端服务
```bash
cd backend
# 启动服务
uvicorn app.main:app --reload --port 8000
```

### 2. 启动前端服务
```bash
cd NotionNext
# 设置后端 URL（可选，默认 http://localhost:8000）
export NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
# 启动服务
npm run dev
```

### 3. 访问创建文章页面

**方式一：通过导航菜单**
- 在网站顶部导航栏点击"创建文章"按钮

**方式二：直接访问 URL**
- 浏览器访问: `http://localhost:3000/create-post`

### 4. 测试流程
1. 填写文章标题、内容等信息
2. 点击"保存文章"按钮
3. 观察成功提示
4. 自动跳转到文章详情页（如 `/en/article/test1`）
5. 验证文章内容、日期等信息正确显示

## API 接口说明

### POST `/api/posts`

**请求体:**
```json
{
  "title": "文章标题",
  "content": "文章内容",
  "tags": ["tag1", "tag2"],
  "slug": "article-slug"  
}
```

**响应:**
```json
{
  "id": 1,
  "title": "文章标题",
  "slug": "article-slug",
  "href": "/article/article-slug",
  "content": "文章内容",
  "summary": "文章摘要...",
  "tags": ["tag1", "tag2"],
  "type": "Post",
  "status": "Published",
  "created_at": "2025-12-23T10:00:00",
  "createdTime": "2025-12-23T10:00:00",
  "date": {
    "start_date": "2025-12-23"
  }
}
```

### GET `/api/post/slug/{slug}`

**用途:** 通过 slug 获取文章详情（前端文章详情页使用）

**响应:** 与 POST `/api/posts` 响应格式相同

## 日期显示修复

### 问题
文章详情页中 "Post on" 和 "Last edited" 显示为空

### 解决方案
在 `[...suffix].js` 和 `index.js` 中添加日期格式化逻辑：

```javascript
// 格式化日期字段，供前端显示使用
const formatDate = (dateStr, lang = 'en-US') => {
  if (!dateStr) return null
  try {
    const date = new Date(dateStr)
    const options = { year: 'numeric', month: 'short', day: 'numeric' }
    const res = date.toLocaleDateString(lang, options)
    // 如果格式是中文日期，则转为横杆
    const format = lang.slice(0, 2).toLowerCase() === 'zh'
      ? res.replace('年', '-').replace('月', '-').replace('日', '')
      : res
    return format
  } catch (e) {
    return null
  }
}

const createdTime = backendPost.created_at
const publishDate = createdTime ? new Date(createdTime).getTime() : null

props.post = {
  // ... 其他字段
  createdTime: createdTime,
  publishDate: publishDate,  // 时间戳，用于格式化显示
  publishDay: formatDate(createdTime, lang),  // 格式化后的日期字符串
  lastEditedTime: createdTime,
  lastEditedDay: formatDate(createdTime, lang),  // 格式化后的日期字符串
  date: backendPost.date || (createdTime ? {
    start_date: createdTime.split('T')[0]
  } : null)
}
```

## n8n Webhook 集成（Day 11 启用）

### 当前状态
- n8n webhook 调用代码已注释
- 代码中已预留 TODO 标记，Day 11 时取消注释即可

### 环境变量配置（Day 11）
```bash
# 在 docker-compose 或环境变量中设置
N8N_WEBHOOK_URL=http://n8n:5678/webhook/blog-save
```

### Webhook Payload 格式
```json
{
  "post_id": 1,
  "title": "文章标题",
  "slug": "article-slug",
  "action": "save",
  "triggered_by": "backend",
  "created_at": "2025-12-23T10:00:00"
}
```

### 启用步骤（Day 11）
1. 取消注释 `backend/app/main.py` 中的 n8n webhook 代码
2. 取消注释 `import httpx` 语句
3. 设置 `N8N_WEBHOOK_URL` 环境变量
4. 测试端到端流程

## 测试

### 手动测试
1. **访问创建页面**
   - 通过导航菜单或直接访问 `http://localhost:3000/create-post`

2. **创建文章**
   - 填写表单并提交
   - 观察成功提示和自动跳转

3. **验证文章显示**
   - 检查文章详情页是否正确显示
   - 验证日期显示（Post on 和 Last edited）
   - 验证文章内容、标签等信息

4. **检查数据库**
   - 查询数据库确认文章已保存
   - 检查后端日志中的创建记录

### API 测试
```bash
# 使用 curl 测试创建接口
curl -X POST http://localhost:8000/api/posts \
  -H "Content-Type: application/json" \
  -d '{
    "title": "测试文章",
    "content": "这是测试内容",
    "tags": ["test", "demo"],
    "slug": "test-article"
  }'

# 测试通过 slug 获取文章
curl http://localhost:8000/api/post/slug/test-article
```

## 问题排查

### 前端无法连接后端
- 检查 `NEXT_PUBLIC_BACKEND_URL` 环境变量
- 检查后端服务是否运行在正确端口（默认 8000）
- 检查 CORS 配置（后端已配置允许所有来源）

### 创建文章后页面空白
- 检查后端日志，确认文章是否成功创建
- 检查文章详情页路由是否正确匹配
- 查看浏览器控制台是否有错误
- 检查后端 API 是否可访问：`curl http://localhost:8000/api/post/slug/{slug}`

### 日期显示为空
- 检查后端返回的 `created_at` 字段格式
- 检查前端日期格式化函数是否正确执行
- 查看浏览器控制台是否有日期解析错误

### 创建文章按钮不显示
- 检查浏览器是否缓存了旧版本（强制刷新 Ctrl+F5）
- 检查主题配置是否正确
- 查看浏览器控制台是否有 JavaScript 错误

### 数据库错误
- 检查数据库连接配置
- 检查表结构是否正确
- 查看数据库日志
- 确认数据库服务是否运行

## 相关文件

### 后端文件
- `backend/app/main.py` - 后端 API 实现
- `backend/app/model.py` - 数据模型定义
- `backend/requirements.txt` - Python 依赖

### 前端文件
- `NotionNext/pages/create-post.js` - 前端创建页面
- `NotionNext/pages/[prefix]/[slug]/[...suffix].js` - 三级路径路由（支持后端文章）
- `NotionNext/pages/[prefix]/[slug]/index.js` - 二级路径路由（支持后端文章）
- `NotionNext/themes/simple/components/MenuList.js` - 导航菜单组件

### 国际化文件
- `NotionNext/lib/lang/en-US.js` - 英文
- `NotionNext/lib/lang/zh-CN.js` - 简体中文
- `NotionNext/lib/lang/zh-TW.js` - 繁体中文（台湾）
- `NotionNext/lib/lang/zh-HK.js` - 繁体中文（香港）
- `NotionNext/lib/lang/ja-JP.js` - 日文
- `NotionNext/lib/lang/fr-FR.js` - 法文
- `NotionNext/lib/lang/tr-TR.js` - 土耳其文

## 完成的功能清单

- ✅ 后端 POST `/api/posts` 接口实现
- ✅ 前端创建文章表单页面
- ✅ 前端与后端 API 联调
- ✅ 表单验证和错误处理
- ✅ 成功提示和自动跳转
- ✅ 创建文章按钮添加到导航菜单
- ✅ 国际化支持（7种语言）
- ✅ 文章详情页支持显示后端文章
- ✅ 修复日期显示问题（publishDay, lastEditedDay）
- ✅ 自动生成 slug 功能
- ✅ 响应式设计和深色模式支持

## 下一步（Day 11）
- 在 n8n 中创建 webhook 工作流
- 取消注释 n8n webhook 调用代码
- 配置 n8n webhook URL
- 测试端到端流程（创建文章 → 触发 n8n → 执行工作流）

## 注意事项

1. **n8n Webhook**: Day 5 阶段不触发 n8n，代码已注释，Day 11 再启用
2. **环境变量**: 前端可通过 `NEXT_PUBLIC_BACKEND_URL` 配置后端地址
3. **路由匹配**: URL `/en/article/{slug}` 会匹配到 `[...suffix].js` 路由
4. **日期格式**: 根据语言设置自动调整日期显示格式
5. **菜单显示**: 创建文章按钮始终显示，不受配置控制
