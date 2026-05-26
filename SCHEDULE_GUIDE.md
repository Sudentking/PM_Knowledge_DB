# 定时任务使用指南

## 启动定时任务

### Windows

**方式1：使用启动脚本（推荐）**
```bash
# 双击运行
start_scheduler.bat

# 或在命令行运行
start_scheduler.bat
```

**方式2：使用任务计划程序**
1. 按 `Win + R`，输入 `taskschd.msc` 打开任务计划程序
2. 点击右侧 "创建基本任务"
3. 名称：`ProductManagerKnowledgeDB`
4. 触发器：选择 "每天"
5. 时间：设置为 `02:00:00`
6. 操作：选择 "启动程序"
   - 程序：`D:\python3.12\python.exe`
   - 参数：`D:\code\Knowledge_DB\scripts\scheduler.py`
7. 完成并勾选 "完成后单击打开属性对话框"
8. 在属性中勾选 "不管用户是否登录都要运行"

**方式3：使用命令行**
```bash
# 创建任务
schtasks /create /tn "ProductManagerKnowledgeDB" /tr "\"D:\python3.12\python.exe\" \"D:\code\Knowledge_DB\scripts\scheduler.py\"" /sc daily /st 02:00 /f

# 验证任务
schtasks /query /tn "ProductManagerKnowledgeDB"
```

## 停止定时任务

### Windows

**方式1：使用任务计划程序**
1. 打开任务计划程序 (`taskschd.msc`)
2. 找到 `ProductManagerKnowledgeDB` 任务
3. 右键点击 → "禁用"

**方式2：使用命令行**
```bash
# 禁用任务
schtasks /change /tn "ProductManagerKnowledgeDB" /disable

# 启用任务
schtasks /change /tn "ProductManagerKnowledgeDB" /enable

# 删除任务
schtasks /delete /tn "ProductManagerKnowledgeDB" /f
```

## 查看任务状态

```bash
# 查看任务详情
schtasks /query /tn "ProductManagerKnowledgeDB" /v

# 查看所有任务
schtasks /query | findstr "ProductManager"
```

## 手动运行一次

```bash
# 立即执行一次工作流
python scripts/workflow.py

# 仅爬取
python scripts/crawler.py

# 仅总结
python scripts/summarizer.py --today

# 查看状态
python scripts/workflow.py --mode status
```

## 修改执行时间

编辑 `config/config.yaml`：
```yaml
schedule:
  enabled: true
  cron: "0 2 * * *"  # 修改这里
  timezone: "Asia/Shanghai"
```

常用cron表达式：
- `0 2 * * *` - 每天凌晨2点
- `0 */6 * * *` - 每6小时一次
- `0 2 * * 1-5` - 工作日凌晨2点
- `0 2 1 * *` - 每月1日凌晨2点

修改后需要重启定时任务。
