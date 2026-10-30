# 凌峰出队助手 v0.3.2

北航凌峰社团出队自用的处理程序，用于根据报名问卷自动安排职能、生成财务报表和购买保险名单，减少领队的重复性工作。

v0.3.0 使用 Tkinter 原生桌面窗口。双击 exe 后直接操作窗口，无需浏览器、不启动网页服务、不占用网络端口。使用者无需安装 Python；全部表格处理在本机完成。获取新版本：https://github.com/maojianhuan/lingfeng_hiking

## v0.3.2 更新

- 修复问卷“是否纯新人”的字段识别及“○学院路”等校区答案解析，缺失信息提示准确到具体字段。
- 新增 macOS Intel、Apple Silicon 和 Linux x86_64 打包，与 Windows 一起自动构建、检查启动并发布。
- 界面字体使用系统默认字体。

## v0.3.1 修复

修复 Windows exe 启动时 `cp_model_helper` DLL 加载失败：打包时显式收集 OR-Tools 的动态库。构建完成后实际运行 exe 的 `--smoke-test`，验证 CP-SAT 求解和 Tkinter 窗口初始化，通过后才上传和发布。

## v0.3.0 更新

- 职能和负责人联合优化：依次优先负责意愿、非新人及全员志愿排名，取消随机分配。
- 装备、后勤、队医负责人必须来自学院路校区。普通队员需至少 5 人，其中学院路成员至少 3 人。
- 报名表新增“校区”（支持“所在校区”）和“是否新人”（是／否）字段；旧表需补全后再自动分配。入学年份不用于判断新人。
- 登山杖、头灯租赁暂全员八折，分别为 9.60 元、6.40 元；Excel 保留原价和折扣参数。
- 当前仅分配大职能与负责人，小职能待任务清单及兼任规则确定后补充。

## 使用方法

1. 从 [Releases](https://github.com/maojianhuan/lingfeng_hiking/releases/latest) 下载 `LingfengFinance.exe`。
2. 双击运行，确认版本获取提示后进入桌面窗口。
3. 点击“导入报名 Excel”，选择问卷星按文本导出的报名明细。
4. 默认选择所有成员，按报名时间排列；单击姓名可取消或重新选择，也可全选、清空。
5. 单选指定领队、副领队和财务。领队、财务必选，副领队可暂不指定；三者不能兼任，更换领队不会清空其他已选人员。
6. 填写包车费（整数元，默认 1000）和对讲机数量（默认 2 台，每台 12 元）。
7. 窗口自动展示职能安排。点击“导出财务与职能报表”或“导出购买保险信息”，在保存对话框中选择位置。

关闭主窗口即退出，无需保留控制台。单文件 exe 首次运行需要解包，可能稍慢。

## 公开测试样例

`data/samples/demo_signup.xlsx` 是按原问卷 29 列结构全新生成的 15 人虚构报名明细，可从仓库下载并直接导入。姓名、入学年份、报名时间、志愿、装备及联系信息均为合成内容，未复制原报名记录。

电话以 `000` 开头，身份证使用无效地区码 `000000`，不能用于实际联系或投保。其他本地 Excel 继续由 Git 忽略，不会纳入仓库。

## 报名表字段

按列名识别，允许增加无关列及调整列顺序，支持原问卷列名前的数字题号。支持的字段包括：

| 标准字段 | 原问卷字段 | 用途 |
| --- | --- | --- |
| 姓名 | 你的姓名 | 导入成员 |
| 报名时间 | 提交答卷时间 | 排列成员 |
| 入学年份 | 年级（不区分大一，研一等称呼，选择入学年级）或年级 | 保留报名信息，不用于判断新人 |
| 校区 | 所在校区 | 限定负责人校区，学院路或学院路校区均可 |
| 是否新人 | 是否纯新人 | 是或否；负责人优先非新人 |
| 职能意向 | 职能志愿 | 按排名分配职能 |
| 是否愿意担任职能负责 | 是否愿意担任职能负责（建议新人积极担任） | 选择负责人 |
| 需要租借的装备 | 同左 | 计算登山杖及头灯费用 |
| 身份证号 | 身份证号（仅用于购买保险） | 保险名单 |
| 手机号 | 联系方式（电话） | 保险名单 |

姓名、报名时间为导入必需字段；报名时间支持 Excel 日期、`YYYY-MM-DD HH:MM:SS` 或问卷的 `YYYY/MM/DD H:MM:SS`。自动分配要求普通成员填写校区和是否新人，不从入学年份推断新人身份。公开样例已包含“所在校区”和“是否纯新人”，可直接导入并分配。缺少保险信息时阻止保险名单导出，可先更正源表后重新导入。

意向支持后勤、队医、装备、摄影、财务、队记，以箭头、顿号或逗号按排名分隔；负责意愿填写“是”或“否”，兼容问卷的“○是”“○否”。没有意向时不计志愿优劣；没有负责意愿时视为不愿负责。没有装备字段时视为未借装备，实际结算请保留问卷的装备借用列。问卷统计汇总不含个人记录，不能作为报名明细导入。

身份证必须在源表中以文本保存。已保存为数值的身份证可能丢失精度，程序会提示更正，不自动修复。重复姓名视为不同报名记录，负责人选择框会用报名位置区分同名者。

## 自动职能安排

领队、副领队及财务手动指定，不参与其他职能分配；财务固定一人。剩余五项职能的人数上限为普通队员人数÷5 向上取整。

使用 OR-Tools CP-SAT 联合分配职能与负责人。每名普通队员承担一项职能，每项职能恰好一名负责人；普通队员至少 5 人，其中至少 3 人来自学院路，分别负责装备、后勤、队医。不满足条件时明确报错，不放宽校区限制。

优化目标按层次依次固定最优值：①最少非自愿负责人；②最少新人负责人；③最低全员志愿排名总损失。第一志愿损失 0，第二志愿 1，依此类推，未列出的职能损失统一为 6。负责意愿目前对所有职能统一生效。因此愿意负责的新人优先于不愿负责的老成员。

同分时按报名时间、原始位置及固定职能顺序逐人确定结果，不随机；同一输入在相同求解器版本下可复现。财务仍手动指定，不参与上述负责人优化。小职能清单及兼任规则尚未确定，本次仅实现大职能与负责人。

预览与 Excel“职能安排”表第一行依次列出领队、副领队、财务，其后每项职能一行，负责人排第一并标注“（职能负责）”。

## 财务与保险导出

每人预收 100 元。普通成员（含财务）收取领队费 10 元，领队及副领队免收；全员保险 2 元；登山杖租赁原价 12 元，头灯原价 8 元；社员享八折，暂无法获取社员名单，因此默认全员八折，实际分别为 9.60 元、6.40 元，按问卷借用记录计算。报表“费用参数”保留原价与 0.8 折扣，装备费用公式引用两者。包车费和对讲机费用全员均摊。

财务文件包含“费用参数”“财务报表”“职能安排”。登山杖和头灯直接显示费用，不单列是否借用。费用及余额使用 Excel 公式，允许负余额；正数退款，负数补缴。分摊保留计算精度，最终余额四舍五入到分，可能产生分币尾差。用 Excel/WPS 打开计算公式，openpyxl 不执行公式计算。

保险名单可独立导出，仅含姓名、身份证号、手机号三列，按报名时间排序，不要求先完成职能安排。身份证号和手机号均以文本导出，保留前导零及证件末尾 X。程序不会修改报名源表，也不允许将报表覆盖到当前源文件。

## 源码运行

使用 Python 3.10 或更新版本，需包含 Tkinter（Windows 和 macOS 的 python.org 官方安装包自带；Linux 发行版可能需安装对应 Tk 支持）。从项目根目录执行：

```bash
python -m pip install -r requirements.txt
python src/launcher.py
```

源码运行需要图形桌面环境；纯 SSH 终端不能直接显示原生窗口。

```text
.
├── src/
│   ├── app.py                    # Tkinter 桌面界面
│   ├── finance.py                # 报名解析及 Excel 导出
│   ├── duties.py                 # 职能分配
│   └── launcher.py               # exe 启动入口及版本提示
├── scripts/build_windows.bat     # Windows 打包
├── .github/workflows/build-windows.yml
├── data/samples/demo_signup.xlsx # 公开虚构样例
├── requirements.txt              # openpyxl 和 OR-Tools；Tkinter 来自 Python
└── requirements-build.txt        # 打包依赖
```

## 本地验证

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

测试覆盖负责人资格、分配可复现性、与小规模穷举结果比较最优性、报名字段解析及装备折扣公式。30 人合成名单在本地一次测得约 0.20 秒，仅供参考。Windows exe 仍需实际桌面操作验证。

## Windows 构建与发布

Windows 10/11 64 位，使用 Python 3.11。双击 `scripts/build_windows.bat` 安装依赖并打包，输出 `dist/LingfengFinance.exe`。使用 `--windowed` 打包为原生窗口，无控制台；不包含 Streamlit 网页运行环境。

GitHub Actions 工作流支持手动运行或推送 `v*` 标签触发。手动运行：仓库 **Actions → Build Desktop Apps → Run workflow**。构建成功后可在 Artifacts 下载 `LingfengFinance-Windows-x64`，ZIP 内包含 exe，保留 30 天。

推送 `v*` 版本标签会在 Windows、macOS（Intel 和 Apple Silicon）、Linux 全部构建及启动检查成功后自动创建对应 Release，并附上四种安装包。手动运行仅生成 Artifacts，不创建 Release。使用内置 `GITHUB_TOKEN` 的 `contents: write` 权限，无需另外配置令牌。

```bash
git add .
git commit -m "描述本次更新"
git push origin main
git tag -a v0.3.2 -m "发布 v0.3.2 跨平台桌面版"
git push origin v0.3.2
```

已发布的标签不重复使用，后续版本更换标签。自动构建不代替 Windows 实际操作验证；测试通过后再面向社团广泛分发。程序不会自动替换用户电脑上的旧 exe，用户需从 Releases 下载新版本。

## Git 管理

默认分支 `main`，远程仓库使用 SSH：`git@github.com:maojianhuan/lingfeng_hiking.git`。版本管理包含源码、文档、构建配置和公开虚构样例；虚拟环境、缓存、构建产物及其他本地 Excel 由 `.gitignore` 排除。

## macOS 使用与构建

Release 提供 macOS ZIP：Apple Silicon（M 系列）选择 `arm64`，Intel Mac 选择 `x86_64`。解压后双击 `LingfengFinance.app`。当前应用未签名或公证；首次打开若被系统拦截，确认下载来源后，在系统设置的“隐私与安全性”中选择“仍要打开”。

本地构建需在对应架构的 Mac 上安装 python.org 的 Python 3.11（包含 Tkinter），从项目根目录运行：

```bash
bash scripts/build_macos.sh
```

输出为 `dist/LingfengFinance.app` 和带架构名的 ZIP。脚本会验证窗口初始化及 CP-SAT 求解器加载。GitHub Actions 的 **Build Desktop Apps** 同时构建 Windows、Intel Mac、Apple Silicon Mac 和 Linux；全部成功后统一发布附件。macOS 界面使用系统默认字体。

## Linux 使用与构建

Linux 提供 `LingfengFinance-Linux-x86_64.tar.gz`，在 Ubuntu 22.04 x86_64 上构建。需要图形桌面环境，面向 glibc 2.35 或更新的发行版；其他发行版尚未实机验证，不支持 Alpine/musl 或 Linux ARM。

解压后保留整个目录，在其中运行：

```bash
tar -xzf LingfengFinance-Linux-x86_64.tar.gz
./LingfengFinance/LingfengFinance
```

无需安装 Python。若从文件管理器启动，打开目录中的 `LingfengFinance` 可执行文件。

本地构建需 Python 3.10+、Tkinter 和图形环境；Ubuntu 可安装 `python3-venv python3-tk`，然后运行：

```bash
bash scripts/build_linux.sh
```

无显示器的构建环境还需安装 `xvfb`，使用 `xvfb-run -a bash scripts/build_linux.sh`。脚本会实际启动打包后的程序，检查 Tk 窗口初始化和 CP-SAT 求解，再生成压缩包。自动检查不代替桌面上的导入、选择和导出操作验证。
