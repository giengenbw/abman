# AB 与 Bestellunterlagen 自动检查工具

本工具用于在本地比较 **Bestellunterlagen（订购资料）** 与 **Auftragsbestätigung，简称 AB（订单确认书）**，自动检查编号、配置 Code、净价、车型、轴距、功率、重量、交期、付款条件和送货地址等内容，并生成 JSON、CSV 及中德双语 HTML 报告。

> **隐私与合规提示**  
> 订单、报价、车辆配置、价格、客户编号、供应商信息、联系人和送货地址通常属于公司机密或个人信息。请仅在公司授权的设备和目录中运行本工具，不要将真实 PDF、检查报告、终端输出或截图上传到公开代码仓库、公共云盘、在线 PDF/OCR 网站或未经公司批准的 AI 服务。

---

## 1. 主要检查规则

工具按照《底盘AB检查 教程》执行以下检查：

1. 检查 Bestellunterlagen 中的 `Angebotsnummer` 与 AB 中的 `Kundenbestellung` 是否一致。
2. 检查 Bestellunterlagen 中所有必须 Code 是否出现在 AB 中。
3. Bestellunterlagen 描述以 `Ohne` 开头或包含 `Ohne` 的缺失 Code，可按规则忽略。
4. AB 中额外出现的 Code 只进行报告，不直接判错。
5. 比较净价、车型、轴距、功率、总重、前后轴载荷、挂车重量、列车总重和交期。
6. 付款条件和送货地址作为人工复核项展示。
7. 生成 JSON、CSV、中文 HTML 和德文 HTML 报告。

自动检查不能代替采购人员的最终审核。尤其是 **SAP 价格、付款条款、交货地址、交期语义和 OCR 识别结果**，仍需人工确认。

---

## 2. 隐私保护要求

### 2.1 只在受控环境中处理文件

建议在以下环境中运行：

- 公司管理的 Windows、macOS 或 Linux 电脑
- 公司批准的加密磁盘或受控网络目录
- 访问权限仅限相关采购人员的文件夹
- 已启用屏幕锁定、磁盘加密和终端安全策略的设备

不建议：

- 在私人电脑上处理真实订单
- 使用在线 PDF 转换、在线 OCR 或在线代码运行网站
- 将输入 PDF 或输出报告放入 Git 仓库
- 通过私人邮箱、私人网盘或公开聊天工具传输文件
- 在工单、Issue、提交信息或截图中暴露订单编号、价格、地址和联系人

### 2.2 输出报告同样属于敏感文件

生成的以下文件可能包含原始文件名、订单编号、价格、配置、地址和付款信息：

- `*.json`
- `*.csv`
- `*_ZH.html`
- `*_DE.html`

检查结束后，应根据公司文件保留政策保存或删除这些文件。若需要分享报告，建议先进行脱敏，例如：

- 隐去订单号、报价号和客户编号
- 删除联系人姓名、电话和邮箱
- 隐去完整送货地址
- 隐去采购价格和付款条件
- 将真实 PDF 文件名改为不含项目或客户信息的内部代号

### 2.3 OCR 注意事项

本工具仅调用本机安装的 `OCRmyPDF` 和 `Tesseract`。请不要为了方便而将公司 PDF 上传到在线 OCR 网站。

使用 OCR 时可能生成临时文件。脚本通过 Python 临时目录处理 OCR 文件，正常结束后会自动清理；如果程序异常中断，应检查系统临时目录是否残留文件，并按公司规定安全删除。

---

## 3. 环境要求

- Python 3.10 或更高版本，建议使用 Python 3.11 或 3.12
- 必需 Python 包：`pypdf`
- 推荐系统工具：`pdftotext`，属于 Poppler 工具集
- 扫描件 OCR，可选：`ocrmypdf` 和 `tesseract`

脚本优先使用 `pdftotext -layout` 提取文本，因为其对部分 MAN PDF 的嵌入字体和表格布局通常更准确。如果系统中没有 `pdftotext`，脚本会回退到 `pypdf`。

---

## 4. 下载并安装 Python

### Windows

1. 从公司软件中心安装 Python，优先使用公司批准的软件源。
2. 如果公司允许从 Python 官方网站下载安装，请在安装时勾选：

```text
Add Python to PATH
```

3. 打开 PowerShell，检查安装：

```powershell
python --version
python -m pip --version
```

如果系统使用 Python Launcher，也可以运行：

```powershell
py --version
py -m pip --version
```

### macOS

建议通过公司软件管理工具安装。安装后检查：

```bash
python3 --version
python3 -m pip --version
```

### Ubuntu 或 Debian

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
python3 --version
```

> 如公司禁止使用管理员权限或外部软件源，请联系 IT 安装，不要绕过公司的安全策略。

---

## 5. 创建项目目录和虚拟环境

将脚本保存为：

```text
ab_bestellunterlagen_checker_v3.py
```

然后在脚本所在目录打开终端。

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

如果 PowerShell 执行策略阻止激活，可使用命令提示符：

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
```

### macOS 或 Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

激活成功后，终端提示符通常会显示 `(.venv)`。

---

## 6. 安装 Python 依赖

### 最小安装

```bash
python -m pip install pypdf
```

也可以在项目根目录创建 `requirements.txt`：

```text
pypdf>=5,<7
```

然后执行：

```bash
python -m pip install -r requirements.txt
```

安装后验证：

```bash
python -c "import pypdf; print(pypdf.__version__)"
```

> 为保证内部使用的一致性，正式部署时建议将测试通过的精确版本固定在 `requirements.txt` 中，例如 `pypdf==6.x.x`。升级依赖后，应使用经过脱敏的测试 PDF 重新验证提取结果。

---

## 7. 安装推荐的 PDF 文本提取工具

### Windows

通过公司软件中心安装 Poppler。如果公司通过 Chocolatey 管理软件，并允许使用，可由 IT 或有权限的人员执行：

```powershell
choco install poppler
```

安装后验证：

```powershell
pdftotext -v
```

### macOS

公司允许使用 Homebrew 时：

```bash
brew install poppler
pdftotext -v
```

### Ubuntu 或 Debian

```bash
sudo apt install poppler-utils
pdftotext -v
```

没有安装 Poppler 时，脚本仍可使用 `pypdf`，但复杂表格或特殊嵌入字体的提取效果可能较差。

---

## 8. 安装 OCR，可选

只有扫描 PDF 或几乎无法提取文字的 PDF 才需要 OCR。

### Ubuntu 或 Debian

```bash
sudo apt install tesseract-ocr tesseract-ocr-deu ocrmypdf
```

### macOS

```bash
brew install tesseract ocrmypdf
```

### Windows

建议由公司 IT 通过受控软件源安装：

- Tesseract OCR
- OCRmyPDF
- Ghostscript，以及 OCRmyPDF 所需的其他组件

验证安装：

```bash
tesseract --version
ocrmypdf --version
```

如输入文件全部是可搜索 PDF，可以不安装 OCR，并在运行时使用 `--no-ocr`。

---

## 9. 运行方法

基本命令：

```bash
python ab_bestellunterlagen_checker_v3.py BESTELLUNG.pdf AB.pdf -o AB_Check_Report
```

示例：

```bash
python ab_bestellunterlagen_checker_v3.py Bestellung_123.pdf AB_123.pdf -o AB_Check_Report
```

建议将输入文件放在不受 Git 跟踪的本地工作目录中。例如：

```text
project/
├── ab_bestellunterlagen_checker_v3.py
├── README.md
├── requirements.txt
└── private_input/          # 真实文件，仅本地保存
    ├── BESTELLUNG.pdf
    └── AB.pdf
```

运行：

```bash
python ab_bestellunterlagen_checker_v3.py private_input/BESTELLUNG.pdf private_input/AB.pdf -o AB_Check_Report
```

### 可用参数

```text
bestellung               Bestellunterlagen PDF
ab                       Auftragsbestätigung PDF
-o, --output             报告基础文件名，默认 AB_Check_Report
--ignore-version         比较编号时忽略末尾 _Vxxx
--no-ocr                 不尝试 OCR
-h, --help               显示帮助
```

查看帮助：

```bash
python ab_bestellunterlagen_checker_v3.py --help
```

### 忽略版本号

默认情况下，编号严格比较。例如：

```text
ABC123_V001 != ABC123_V002
```

如果业务规则允许忽略末尾 `_Vxxx`，使用：

```bash
python ab_bestellunterlagen_checker_v3.py BESTELLUNG.pdf AB.pdf -o AB_Check_Report --ignore-version
```

启用后：

```text
ABC123_V001 == ABC123_V002
```

仅在内部规则明确允许时使用此选项。

### 禁用 OCR

```bash
python ab_bestellunterlagen_checker_v3.py BESTELLUNG.pdf AB.pdf -o AB_Check_Report --no-ocr
```

如果 PDF 几乎没有可提取文本，禁用 OCR 后程序将提示先转换为可搜索 PDF。

---

## 10. 输出文件

假设使用：

```bash
-o AB_Check_Report
```

将生成：

```text
AB_Check_Report.json
AB_Check_Report.csv
AB_Check_Report_ZH.html
AB_Check_Report_DE.html
```

### JSON

适合程序读取、留档或后续自动处理，包含：

- 总体结论
- 两份文件提取出的字段
- 每项检查状态
- 缺失的必需 Code
- 按 `Ohne` 规则忽略的 Code
- AB 中额外出现的 Code
- 已知限制

### CSV

适合使用 Excel 打开并筛选。CSV 使用 `UTF-8 with BOM` 编码，以改善中文在 Excel 中的显示。

### 中文 HTML

```text
AB_Check_Report_ZH.html
```

用于采购人员阅读和人工复核。

### 德文 HTML

```text
AB_Check_Report_DE.html
```

可用于内部德文沟通或与供应商澄清前的检查。

> 报告可能包含公司敏感数据。打开、转发和保存报告时，应按照与原始订单 PDF 相同的保护等级处理。

---

## 11. 状态和退出码

### 检查状态

- `OK`：自动检查一致
- `ERROR`：发现明确不一致或缺少必需内容
- `WARNING`：未提取到值，或只能进行宽松比较
- `REVIEW`：必须人工审核，例如付款条件和送货地址

### 总体结论

- `不正确/需供应商澄清`：至少存在一个 `ERROR`
- `需人工复核`：没有 `ERROR`，但存在 `WARNING` 或 `REVIEW`
- `正确`：所有自动检查项均通过，且没有待复核项

由于付款条件和送货地址目前固定为 `REVIEW`，实际报告通常至少会显示“需人工复核”。

### 程序退出码

- `0`：没有 `ERROR`
- `2`：至少存在一个 `ERROR`，或命令行参数检查失败
- 其他非零值：运行异常，例如依赖缺失、PDF 损坏或 OCR 执行失败

在自动化流程中，可以根据退出码判断是否存在明确错误。

#### Windows PowerShell

```powershell
python ab_bestellunterlagen_checker_v3.py BESTELLUNG.pdf AB.pdf -o AB_Check_Report
$LASTEXITCODE
```

#### macOS 或 Linux

```bash
python ab_bestellunterlagen_checker_v3.py BESTELLUNG.pdf AB.pdf -o AB_Check_Report
echo $?
```

---

## 12. 人工复核清单

即使自动结果没有 `ERROR`，仍建议逐项确认：

1. SAP 中的最终订单价格是否与 AB 一致。
2. 付款条件是否新增 `vor Zulassung`、预付款或其他限制。
3. 公司名称、街道、邮编、城市和 `Tor` 信息是否正确。
4. 交期的月份、周次、年份和“预计/不具约束力”等语义是否一致。
5. Code 描述中的 `Ohne` 是否确实适用于“缺失可忽略”的业务规则。
6. AB 中额外 Code 是否合理，是否会增加成本或改变配置。
7. 扫描件或 OCR 是否把字母 `O`、数字 `0`、字母 `I`、数字 `1` 混淆。
8. 多车辆、多版本或多价格文件是否被脚本错误地只提取了第一个匹配值。
9. 载荷表中的“国家许可值”“技术值”和“Technical Load Plus”列是否比较了正确的一列。

---

## 13. `.gitignore` 隐私保护配置

请在项目根目录创建 `.gitignore`，至少加入以下内容：

```gitignore
# PDF
*.pdf

# Excel
*.xls
*.xlsx
*.xlsm
*.xlsb
~$*.xls
~$*.xlsx

# Reports
report.*
AB_Check_Report.*
*_ZH.html
*_DE.html

# Private working directories
private_input/
private_output/

# Python
__pycache__/
*.pyc

# Virtual Environment
.venv/
venv/
env/

# VS Code
.vscode/

# Operating system files
.DS_Store
Thumbs.db
```

注意：`.gitignore` 只能阻止尚未被 Git 跟踪的文件。若敏感文件已经提交过，单纯添加 `.gitignore` 不会将其从历史记录中删除。

检查 Git 即将提交的内容：

```bash
git status
```

如果 PDF 或报告已被加入暂存区，但尚未提交：

```bash
git restore --staged path/to/sensitive-file.pdf
```

如果文件已经被 Git 跟踪，但希望今后停止跟踪，同时保留本地文件：

```bash
git rm --cached path/to/sensitive-file.pdf
```

如果敏感信息已推送到远程仓库，应立即：

1. 停止继续分享仓库。
2. 通知公司 IT、信息安全或数据保护负责人。
3. 按公司流程清理 Git 历史和远程副本。
4. 如泄露内容包含账号、访问令牌或密码，立即撤销并轮换。

不要只删除最新提交，因为敏感文件可能仍保留在 Git 历史中。

---

## 14. 源代码保存注意事项

聊天工具或网页复制代码时，可能把 Python 运算符转义为 HTML 实体。例如：

```text
&lt;    可能被显示为 &amp;lt;
&gt;    可能被显示为 &amp;gt;
```

Python 文件中必须保存为真实运算符。例如：

```python
if visible >= 200:
    return pages
```

而不能保存为：

```python
if visible &gt;= 200:
    return pages
```

保存脚本后，先进行语法检查：

```bash
python -m py_compile ab_bestellunterlagen_checker_v3.py
```

如果没有输出，通常表示语法检查通过。

---

## 15. 常见问题

### 提示缺少 `pypdf`

```text
缺少 pypdf。请安装: pip install pypdf
```

请确认虚拟环境已激活，然后运行：

```bash
python -m pip install pypdf
```

### PDF 几乎没有可提取文本

原因通常是 PDF 为扫描件。可选择：

- 在本机安装 OCRmyPDF 和 Tesseract
- 由公司批准的软件将其转换为可搜索 PDF
- 人工检查文件

不要将公司文件上传到在线 OCR 服务。

### OCR 已安装但命令找不到

检查：

```bash
ocrmypdf --version
tesseract --version
```

如果命令不存在，请联系 IT 检查安装路径和 `PATH` 环境变量。

### 金额或字段提取错误

可能原因：

- PDF 表格布局特殊
- 字体嵌入方式异常
- 一个文件中存在多个金额
- OCR 把数字识别错误
- 字段名称与正则表达式不匹配

建议先查看 HTML 报告中的原始提取值，再对照 PDF 人工核验。不要仅根据总体状态向供应商发出澄清。

### Code 被错误识别

当前 Code 规则主要识别以下格式：

```text
0P...
DE...
ZLS..
ZS...
ZF...
```

如果供应商使用新的 Code 格式，需要更新脚本中的 `CODE_RE`，并使用脱敏测试文件回归验证。

### HTML 报告打不开

HTML 是本地文件，可以用 Edge、Chrome 或 Firefox 打开。不要将报告上传到在线 HTML 预览网站。

---

## 16. 建议的安全测试方式

开发和测试时，请使用人工构造或彻底脱敏的数据：

- 订单号改为 `TEST-001`
- 报价号改为 `ANGEBOT-TEST`
- 公司名改为 `Musterfirma GmbH`
- 地址改为通用测试地址
- 联系人改为虚构名称
- 金额改为非真实测试金额

脱敏时不要只遮住 PDF 可见区域。PDF 中可能仍保留文本层、批注、附件和元数据。对外分享测试文件前，应使用公司批准的脱敏工具，并再次提取文本确认原信息已真正删除。

---

## 17. 已知限制

- 无法直接访问或核对 SAP 中的数据。
- 正则表达式依赖当前 MAN/Daimler 文档格式，模板升级后可能需要调整。
- OCR 可能误识别字符、金额和 Code。
- 同一 PDF 中包含多个订单、车辆或版本时，部分字段可能只提取第一个匹配值。
- 付款条件、送货地址和交期可能存在语义相同但文本不同的情况。
- `Ohne` 判断基于 Code 附近的描述，复杂换行可能导致误判。
- AB 中额外 Code 不自动判错，但额外配置可能影响价格、交期或车辆规格，必须抽查。

---

## 18. 最小快速开始

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install pypdf
python -m py_compile ab_bestellunterlagen_checker_v3.py
python ab_bestellunterlagen_checker_v3.py private_input\BESTELLUNG.pdf private_input\AB.pdf -o AB_Check_Report
```

### macOS 或 Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install pypdf
python -m py_compile ab_bestellunterlagen_checker_v3.py
python ab_bestellunterlagen_checker_v3.py private_input/BESTELLUNG.pdf private_input/AB.pdf -o AB_Check_Report
```

运行完成后，优先打开：

```text
AB_Check_Report_ZH.html
```

然后对所有 `ERROR`、`WARNING` 和 `REVIEW` 项进行人工核验。

---

## 19. 责任说明

本工具是内部辅助检查工具，不构成对订单、合同、价格、交期或技术配置的最终确认。自动报告中的“正确”仅表示脚本在可提取文本和既定规则范围内未发现差异。最终放单、供应商澄清和 SAP 操作仍应由具有相应权限的人员按照公司流程完成。
