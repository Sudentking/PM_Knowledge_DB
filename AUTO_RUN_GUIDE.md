# 自动运行配置指南

## 方式1: Windows任务计划程序（推荐）

### 步骤1: 打开任务计划程序

1. 按 `Win + R`，输入 `taskschd.msc`，回车
2. 或者搜索"任务计划程序"

### 步骤2: 创建基本任务

1. 右侧点击 "创建基本任务"
2. 名称: `知识库自动更新`
3. 描述: `每天自动爬取和总结产品经理文章`

### 步骤3: 设置触发器

1. 选择 "每天"
2. 开始时间: `02:00:00`（凌晨2点）
3. 每隔 `1` 天

### 步骤4: 设置操作

1. 选择 "启动程序"
2. 程序或脚本: `D:\code\Knowledge_DB\run_workflow.bat`
3. 起始于: `D:\code\Knowledge_DB`

### 步骤5: 完成设置

1. 勾选 "当单击完成时，打开此任务属性对话框"
2. 点击 "完成"
3. 在属性对话框中：
   - 勾选 "不管用户是否登录都要运行"
   - 勾选 "使用最高权限运行"
   - 配置: 选择 "Windows 10"

### 验证任务

1. 在任务计划程序库中找到 "知识库自动更新"
2. 右键 → "运行" 测试

---

## 方式2: 使用Python直接运行

### 手动运行

```bash
cd D:\code\Knowledge_DB
python scripts/run_scheduled.py
```

### 带参数运行

```bash
# 仅爬取
python scripts/workflow.py --mode crawl

# 仅总结
python scripts/workflow.py --mode summarize

# 仅Git操作
python scripts/workflow.py --mode git

# 查看状态
python scripts/workflow.py --mode status
```

---

## 方式3: 使用批处理文件

### 直接运行

```bash
cd D:\code\Knowledge_DB
run_workflow.bat
```

### 手动创建定时任务（命令行）

```bash
schtasks /create /tn "知识库自动更新" /tr "D:\code\Knowledge_DB\run_workflow.bat" /sc daily /st 02:00 /f
```

---

## 日志说明

### 日志位置

- 主日志: `logs/crawler.log`
- 每日运行日志: `logs/workflow_YYYY-MM-DD.log`
- 批处理日志: `logs/workflow_run.log`

### 查看日志

```bash
# 查看最新日志
tail -f logs/crawler.log

# 查看今天的运行日志
cat logs/workflow_2026-05-27.log

# 查看运行历史
cat logs/workflow_run.log
```

### 日志内容

每次运行记录：
- 运行时间
- 爬取文章数量
- 总结文章数量
- 重命名文章数量
- 运行耗时
- 错误信息（如有）

---

## 运行模式说明

| 模式 | 命令 | 说明 |
|------|------|------|
| full | `--mode full` | 完整流程：爬取→总结→重命名→Git推送 |
| crawl | `--mode crawl` | 仅爬取新文章 |
| summarize | `--mode summarize` | 仅总结未处理的文章 |
| git | `--mode git` | 仅执行Git提交和推送 |
| status | `--mode status` | 查看系统状态 |

---

## 常见问题

### Q: 如何开启/关闭自动运行？

**开启**:
1. 打开任务计划程序
2. 找到 "知识库自动更新"
3. 右键 → "启用"

**关闭**:
1. 打开任务计划程序
2. 找到 "知识库自动更新"
3. 右键 → "禁用"

### Q: 如何修改运行时间？

1. 打开任务计划程序
2. 找到 "知识库自动更新"
3. 右键 → "属性"
4. "触发器" 选项卡 → "编辑"
5. 修改时间

### Q: 运行失败怎么办？

1. 查看日志: `logs/workflow_YYYY-MM-DD.log`
2. 检查网络连接
3. 检查API Key是否有效
4. 手动运行测试: `python scripts/workflow.py --mode status`

### Q: 如何只运行一次测试？

```bash
cd D:\code\Knowledge_DB
python scripts/run_scheduled.py
```

---

## 快速配置脚本

创建定时任务的PowerShell脚本：

```powershell
# 保存为 setup_schedule.ps1，以管理员身份运行

$Action = New-ScheduledTaskAction -Execute "D:\code\Knowledge_DB\run_workflow.bat" -WorkingDirectory "D:\code\Knowledge_DB"
$Trigger = New-ScheduledTaskTrigger -Daily -At 2am
$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopOnIdleEnd
$Principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

Register-ScheduledTask -TaskName "知识库自动更新" -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Description "每天自动爬取和总结产品经理文章"
```

运行方式：
```powershell
# 以管理员身份打开PowerShell，执行
.\setup_schedule.ps1
```
