# AB- und Bestellunterlagen-Prüfer / AB 与订购资料自动检查工具

Dieses lokale Werkzeug vergleicht **Bestellunterlagen** mit einer **Auftragsbestätigung (AB)**. Es prüft unter anderem Nummern, Konfigurationscodes, Nettopreis, Fahrzeugtyp, Radstand, Leistung, Gewichte, Liefertermin, Zahlungsbedingungen und Lieferadresse. Anschließend erzeugt es Berichte im JSON-, CSV- sowie zweisprachigen HTML-Format.

本地工具用于比较 **Bestellunterlagen（订购资料）** 与 **Auftragsbestätigung，简称 AB（订单确认书）**。工具自动检查编号、配置 Code、净价、车型、轴距、功率、重量、交期、付款条件和送货地址等内容，并生成 JSON、CSV 以及中德双语 HTML 报告。

> **Datenschutz- und Compliance-Hinweis / 隐私与合规提示**  
> Bestellungen, Angebote, Fahrzeugkonfigurationen, Preise, Kundennummern, Lieferantendaten, Ansprechpartner und Lieferadressen sind in der Regel vertrauliche Unternehmens- oder personenbezogene Daten. Verwenden Sie das Werkzeug ausschließlich auf autorisierten Unternehmensgeräten und in freigegebenen Verzeichnissen. Laden Sie echte PDF-Dateien, Prüfberichte, Terminalausgaben oder Screenshots nicht in öffentliche Code-Repositories, öffentliche Cloudspeicher, Online-PDF-/OCR-Dienste oder nicht freigegebene KI-Dienste hoch.  
> 订单、报价、车辆配置、价格、客户编号、供应商信息、联系人和送货地址通常属于公司机密或个人信息。请仅在公司授权的设备和目录中运行本工具，不要将真实 PDF、检查报告、终端输出或截图上传到公开代码仓库、公共云盘、在线 PDF/OCR 网站或未经公司批准的 AI 服务。

---

## Inhaltsverzeichnis / 目录

1. [Prüfregeln / 主要检查规则](#1-prüfregeln--主要检查规则)
2. [Datenschutz / 隐私保护要求](#2-datenschutz--隐私保护要求)
3. [Systemanforderungen / 环境要求](#3-systemanforderungen--环境要求)
4. [Python installieren / 安装-Python](#4-python-installieren--安装-python)
5. [Projekt und virtuelle Umgebung / 项目目录和虚拟环境](#5-projekt-und-virtuelle-umgebung--项目目录和虚拟环境)
6. [Python-Abhängigkeiten / Python-依赖](#6-python-abhängigkeiten--python-依赖)
7. [PDF-Textextraktion / PDF-文本提取工具](#7-pdf-textextraktion--pdf-文本提取工具)
8. [OCR, optional / OCR，可选](#8-ocr-optional--ocr可选)
9. [Verwendung / 运行方法](#9-verwendung--运行方法)
10. [Ausgabedateien / 输出文件](#10-ausgabedateien--输出文件)
11. [Status und Exit-Codes / 状态和退出码](#11-status-und-exit-codes--状态和退出码)
12. [Manuelle Prüfliste / 人工复核清单](#12-manuelle-prüfliste--人工复核清单)
13. [.gitignore und Datenschutz / 隐私保护配置](#13-gitignore-und-datenschutz--隐私保护配置)
14. [Hinweise zum Quellcode / 源代码保存注意事项](#14-hinweise-zum-quellcode--源代码保存注意事项)
15. [Häufige Probleme / 常见问题](#15-häufige-probleme--常见问题)
16. [Sicher testen / 安全测试方式](#16-sicher-testen--安全测试方式)
17. [Bekannte Einschränkungen / 已知限制](#17-bekannte-einschränkungen--已知限制)
18. [Schnellstart / 最小快速开始](#18-schnellstart--最小快速开始)
19. [Haftungsausschluss / 责任说明](#19-haftungsausschluss--责任说明)

---

## 1. Prüfregeln / 主要检查规则

Das Werkzeug führt die Prüfungen gemäß der internen Anleitung **„底盘AB检查 教程“** durch:

工具按照内部《底盘AB检查 教程》执行以下检查：

1. Die `Angebotsnummer` in den Bestellunterlagen wird mit der `Kundenbestellung` in der AB verglichen.  
   检查 Bestellunterlagen 中的 `Angebotsnummer` 与 AB 中的 `Kundenbestellung` 是否一致。
2. Alle Pflicht-Codes aus den Bestellunterlagen müssen in der AB vorhanden sein.  
   检查 Bestellunterlagen 中所有必须 Code 是否出现在 AB 中。
3. Fehlende Codes können ignoriert werden, wenn die zugehörige Beschreibung mit `Ohne` beginnt oder `Ohne` enthält und die interne Regel dies zulässt.  
   Bestellunterlagen 描述以 `Ohne` 开头或包含 `Ohne` 的缺失 Code，可按规则忽略。
4. Zusätzliche Codes in der AB werden gemeldet, aber nicht automatisch als Fehler bewertet.  
   AB 中额外出现的 Code 只进行报告，不直接判错。
5. Verglichen werden Nettopreis, Fahrzeugtyp, Radstand, Leistung, Gesamtgewicht, Vorder- und Hinterachslast, Anhängelast, Zuggesamtgewicht und Liefertermin.  
   比较净价、车型、轴距、功率、总重、前后轴载荷、挂车重量、列车总重和交期。
6. Zahlungsbedingungen und Lieferadresse werden als manuell zu prüfende Punkte angezeigt.  
   付款条件和送货地址作为人工复核项展示。
7. Das Werkzeug erzeugt JSON-, CSV-, chinesische HTML- und deutsche HTML-Berichte.  
   生成 JSON、CSV、中文 HTML 和德文 HTML 报告。

> Die automatische Prüfung ersetzt nicht die abschließende Kontrolle durch den Einkauf. Insbesondere **SAP-Preis, Zahlungsbedingungen, Lieferadresse, Bedeutung des Liefertermins und OCR-Ergebnisse** müssen weiterhin manuell geprüft werden.  
> 自动检查不能代替采购人员的最终审核。尤其是 **SAP 价格、付款条款、交货地址、交期语义和 OCR 识别结果**，仍需人工确认。

---

## 2. Datenschutz / 隐私保护要求

### 2.1 Dateien nur in kontrollierten Umgebungen verarbeiten / 只在受控环境中处理文件

**Empfohlen / 建议：**

- Vom Unternehmen verwaltete Windows-, macOS- oder Linux-Geräte  
  公司管理的 Windows、macOS 或 Linux 电脑
- Freigegebene verschlüsselte Datenträger oder kontrollierte Netzwerkverzeichnisse  
  公司批准的加密磁盘或受控网络目录
- Ordner, auf die nur zuständige Einkaufsmitarbeiter Zugriff haben  
  访问权限仅限相关采购人员的文件夹
- Geräte mit Bildschirmsperre, Datenträgerverschlüsselung und Terminal-Sicherheitsrichtlinien  
  已启用屏幕锁定、磁盘加密和终端安全策略的设备

**Nicht empfohlen / 不建议：**

- Echte Bestellungen auf privaten Computern verarbeiten  
  在私人电脑上处理真实订单
- Online-PDF-Konverter, Online-OCR oder Online-Codeausführung verwenden  
  使用在线 PDF 转换、在线 OCR 或在线代码运行网站
- Eingabe-PDFs oder Berichte in Git-Repositories ablegen  
  将输入 PDF 或输出报告放入 Git 仓库
- Dateien über private E-Mail-Konten, private Cloudspeicher oder öffentliche Chats übertragen  
  通过私人邮箱、私人网盘或公开聊天工具传输文件
- Bestellnummern, Preise, Adressen oder Ansprechpartner in Tickets, Issues, Commit-Nachrichten oder Screenshots offenlegen  
  在工单、Issue、提交信息或截图中暴露订单编号、价格、地址和联系人

### 2.2 Berichte sind ebenfalls vertraulich / 输出报告同样属于敏感文件

Folgende Dateien können ursprüngliche Dateinamen, Bestellnummern, Preise, Konfigurationen, Adressen und Zahlungsinformationen enthalten:

以下文件可能包含原始文件名、订单编号、价格、配置、地址和付款信息：

- `*.json`
- `*.csv`
- `*_ZH.html`
- `*_DE.html`

Speichern oder löschen Sie diese Dateien nach Abschluss der Prüfung gemäß den Aufbewahrungsrichtlinien des Unternehmens. Vor einer Weitergabe sollten Berichte anonymisiert werden:

检查结束后，应根据公司文件保留政策保存或删除这些文件。若需要分享报告，建议先进行脱敏：

- Bestell-, Angebots- und Kundennummern unkenntlich machen  
  隐去订单号、报价号和客户编号
- Namen, Telefonnummern und E-Mail-Adressen entfernen  
  删除联系人姓名、电话和邮箱
- Vollständige Lieferadresse ausblenden  
  隐去完整送货地址
- Einkaufspreise und Zahlungsbedingungen ausblenden  
  隐去采购价格和付款条件
- Reale PDF-Dateinamen durch interne neutrale Kennungen ersetzen  
  将真实 PDF 文件名改为不含项目或客户信息的内部代号

### 2.3 OCR-Hinweise / OCR 注意事项

Das Werkzeug verwendet ausschließlich lokal installierte Programme wie `OCRmyPDF` und `Tesseract`. Unternehmens-PDFs dürfen nicht auf Online-OCR-Websites hochgeladen werden.

本工具仅调用本机安装的 `OCRmyPDF` 和 `Tesseract`。请不要为了方便而将公司 PDF 上传到在线 OCR 网站。

Bei der OCR-Verarbeitung können temporäre Dateien entstehen. Das Skript verarbeitet sie im temporären Python-Verzeichnis und entfernt sie bei normalem Programmende automatisch. Nach einem Abbruch sollte das Systemverzeichnis für temporäre Dateien kontrolliert und gemäß Unternehmensrichtlinie sicher bereinigt werden.

使用 OCR 时可能生成临时文件。脚本通过 Python 临时目录处理 OCR 文件，正常结束后会自动清理；如果程序异常中断，应检查系统临时目录是否残留文件，并按公司规定安全删除。

---

## 3. Systemanforderungen / 环境要求

- Python 3.10 oder neuer, empfohlen: Python 3.11 oder 3.12  
  Python 3.10 或更高版本，建议使用 Python 3.11 或 3.12
- Erforderliches Python-Paket: `pypdf`  
  必需 Python 包：`pypdf`
- Empfohlenes Systemwerkzeug: `pdftotext` aus dem Poppler-Paket  
  推荐系统工具：`pdftotext`，属于 Poppler 工具集
- Optional für gescannte Dokumente: `ocrmypdf` und `tesseract`  
  扫描件 OCR，可选：`ocrmypdf` 和 `tesseract`

Das Skript bevorzugt `pdftotext -layout`, weil damit eingebettete Schriftarten und Tabellenlayouts in manchen MAN-PDFs zuverlässiger extrahiert werden. Ohne `pdftotext` wird automatisch auf `pypdf` zurückgegriffen.

脚本优先使用 `pdftotext -layout` 提取文本，因为其对部分 MAN PDF 的嵌入字体和表格布局通常更准确。如果系统中没有 `pdftotext`，脚本会回退到 `pypdf`。

---

## 4. Python installieren / 安装 Python

### Windows

1. Installieren Sie Python nach Möglichkeit über das Software-Center des Unternehmens.  
   优先从公司软件中心安装 Python。
2. Wenn die Installation über die offizielle Python-Website freigegeben ist, aktivieren Sie während der Installation:  
   如果公司允许从 Python 官方网站下载安装，请在安装时勾选：

```text
Add Python to PATH
```

3. Installation in PowerShell prüfen / 在 PowerShell 中检查安装：

```powershell
python --version
python -m pip --version
```

Alternativ mit Python Launcher / 如果系统使用 Python Launcher：

```powershell
py --version
py -m pip --version
```

### macOS

Installation möglichst über die Softwareverwaltung des Unternehmens durchführen und anschließend prüfen:

建议通过公司软件管理工具安装。安装后检查：

```bash
python3 --version
python3 -m pip --version
```

### Ubuntu oder Debian / Ubuntu 或 Debian

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
python3 --version
```

> Falls Administratorrechte oder externe Softwarequellen nicht erlaubt sind, wenden Sie sich an die IT. Unternehmensrichtlinien dürfen nicht umgangen werden.  
> 如公司禁止使用管理员权限或外部软件源，请联系 IT 安装，不要绕过公司的安全策略。

---

## 5. Projekt und virtuelle Umgebung / 项目目录和虚拟环境

Speichern Sie das Skript unter folgendem Namen / 将脚本保存为：

```text
ab_bestellunterlagen_checker_v3.py
```

Öffnen Sie danach ein Terminal im Skriptverzeichnis.  
然后在脚本所在目录打开终端。

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

Falls die PowerShell-Ausführungsrichtlinie die Aktivierung verhindert, verwenden Sie die Eingabeaufforderung:

如果 PowerShell 执行策略阻止激活，可使用命令提示符：

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
```

### macOS oder Linux / macOS 或 Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

Nach erfolgreicher Aktivierung zeigt die Eingabeaufforderung normalerweise `(.venv)` an.  
激活成功后，终端提示符通常会显示 `(.venv)`。

---

## 6. Python-Abhängigkeiten / Python 依赖

### Minimalinstallation / 最小安装

```bash
python -m pip install pypdf
```

Alternativ im Projektstamm eine Datei `requirements.txt` anlegen:  
也可以在项目根目录创建 `requirements.txt`：

```text
pypdf>=5,<7
```

Danach installieren / 然后执行：

```bash
python -m pip install -r requirements.txt
```

Installation prüfen / 安装后验证：

```bash
python -c "import pypdf; print(pypdf.__version__)"
```

> Für einen reproduzierbaren internen Betrieb sollte nach erfolgreichem Test eine exakte Version festgelegt werden, zum Beispiel `pypdf==6.x.x`. Nach jedem Upgrade sind die Extraktionsergebnisse erneut mit anonymisierten Test-PDFs zu prüfen.  
> 为保证内部使用的一致性，正式部署时建议将测试通过的精确版本固定在 `requirements.txt` 中，例如 `pypdf==6.x.x`。升级依赖后，应使用经过脱敏的测试 PDF 重新验证提取结果。

---

## 7. PDF-Textextraktion / PDF 文本提取工具

### Windows

Installieren Sie Poppler über das Software-Center des Unternehmens. Falls Chocolatey zentral verwaltet wird und dessen Verwendung erlaubt ist, kann die IT oder eine berechtigte Person Folgendes ausführen:

通过公司软件中心安装 Poppler。如果公司通过 Chocolatey 管理软件，并允许使用，可由 IT 或有权限的人员执行：

```powershell
choco install poppler
```

Prüfen / 验证：

```powershell
pdftotext -v
```

### macOS

```bash
brew install poppler
pdftotext -v
```

### Ubuntu oder Debian / Ubuntu 或 Debian

```bash
sudo apt install poppler-utils
pdftotext -v
```

Ohne Poppler kann das Skript weiterhin `pypdf` verwenden. Bei komplexen Tabellen oder ungewöhnlich eingebetteten Schriftarten kann die Extraktionsqualität jedoch geringer sein.

没有安装 Poppler 时，脚本仍可使用 `pypdf`，但复杂表格或特殊嵌入字体的提取效果可能较差。

---

## 8. OCR, optional / OCR，可选

OCR ist nur bei gescannten oder nahezu nicht auslesbaren PDF-Dateien erforderlich.  
只有扫描 PDF 或几乎无法提取文字的 PDF 才需要 OCR。

### Ubuntu oder Debian / Ubuntu 或 Debian

```bash
sudo apt install tesseract-ocr tesseract-ocr-deu ocrmypdf
```

### macOS

```bash
brew install tesseract ocrmypdf
```

### Windows

Die Installation sollte durch die IT aus freigegebenen Quellen erfolgen:  
建议由公司 IT 通过受控软件源安装：

- Tesseract OCR
- OCRmyPDF
- Ghostscript und weitere erforderliche OCRmyPDF-Komponenten  
  Ghostscript，以及 OCRmyPDF 所需的其他组件

Installation prüfen / 验证安装：

```bash
tesseract --version
ocrmypdf --version
```

Wenn alle Eingabedateien durchsuchbare PDFs sind, kann OCR entfallen. Verwenden Sie dann `--no-ocr`.  
如输入文件全部是可搜索 PDF，可以不安装 OCR，并在运行时使用 `--no-ocr`。

---

## 9. Verwendung / 运行方法

Grundbefehl / 基本命令：

```bash
python ab_bestellunterlagen_checker_v3.py BESTELLUNG.pdf AB.pdf -o AB_Check_Report
```

Beispiel / 示例：

```bash
python ab_bestellunterlagen_checker_v3.py Bestellung_123.pdf AB_123.pdf -o AB_Check_Report
```

Eingabedateien sollten in einem lokalen, nicht von Git verfolgten Arbeitsverzeichnis liegen:  
建议将输入文件放在不受 Git 跟踪的本地工作目录中：

```text
project/
├── ab_bestellunterlagen_checker_v3.py
├── README.md
├── requirements.txt
└── private_input/          # Echte Dateien, nur lokal / 真实文件，仅本地保存
    ├── BESTELLUNG.pdf
    └── AB.pdf
```

Ausführen / 运行：

```bash
python ab_bestellunterlagen_checker_v3.py private_input/BESTELLUNG.pdf private_input/AB.pdf -o AB_Check_Report
```

### Parameter / 可用参数

```text
bestellung               Bestellunterlagen-PDF / Bestellunterlagen PDF
ab                       Auftragsbestätigungs-PDF / Auftragsbestätigung PDF
-o, --output             Basisname der Berichte, Standard: AB_Check_Report
                         报告基础文件名，默认 AB_Check_Report
--ignore-version         Suffix _Vxxx beim Nummernvergleich ignorieren
                         比较编号时忽略末尾 _Vxxx
--no-ocr                 Keine OCR versuchen / 不尝试 OCR
-h, --help               Hilfe anzeigen / 显示帮助
```

Hilfe anzeigen / 查看帮助：

```bash
python ab_bestellunterlagen_checker_v3.py --help
```

### Versionsnummer ignorieren / 忽略版本号

Standardmäßig werden Nummern streng verglichen:  
默认情况下，编号严格比较：

```text
ABC123_V001 != ABC123_V002
```

Wenn die interne Regel das Ignorieren des Suffixes `_Vxxx` zulässt:  
如果业务规则允许忽略末尾 `_Vxxx`：

```bash
python ab_bestellunterlagen_checker_v3.py BESTELLUNG.pdf AB.pdf -o AB_Check_Report --ignore-version
```

Dann gilt / 启用后：

```text
ABC123_V001 == ABC123_V002
```

Diese Option darf nur verwendet werden, wenn die interne Regel dies ausdrücklich erlaubt.  
仅在内部规则明确允许时使用此选项。

### OCR deaktivieren / 禁用 OCR

```bash
python ab_bestellunterlagen_checker_v3.py BESTELLUNG.pdf AB.pdf -o AB_Check_Report --no-ocr
```

Enthält die PDF-Datei nahezu keinen extrahierbaren Text, fordert das Programm dazu auf, sie zunächst in eine durchsuchbare PDF umzuwandeln.  
如果 PDF 几乎没有可提取文本，禁用 OCR 后程序将提示先转换为可搜索 PDF。

---

## 10. Ausgabedateien / 输出文件

Bei Verwendung von `-o AB_Check_Report` werden folgende Dateien erzeugt:  
假设使用 `-o AB_Check_Report`，将生成：

```text
AB_Check_Report.json
AB_Check_Report.csv
AB_Check_Report_ZH.html
AB_Check_Report_DE.html
```

### JSON

Für maschinelle Verarbeitung, Archivierung oder Folgeautomatisierung. Enthalten sind Gesamtbewertung, extrahierte Felder, Einzelstatus, fehlende Pflicht-Codes, nach der `Ohne`-Regel ignorierte Codes, zusätzliche AB-Codes und bekannte Einschränkungen.

适合程序读取、留档或后续自动处理，包含总体结论、两份文件提取出的字段、每项检查状态、缺失的必需 Code、按 `Ohne` 规则忽略的 Code、AB 中额外出现的 Code 和已知限制。

### CSV

Für Excel und Filterfunktionen. Die Datei wird als `UTF-8 with BOM` gespeichert, damit chinesische Zeichen in Excel zuverlässiger angezeigt werden.

适合使用 Excel 打开并筛选。CSV 使用 `UTF-8 with BOM` 编码，以改善中文在 Excel 中的显示。

### Chinesischer HTML-Bericht / 中文 HTML

```text
AB_Check_Report_ZH.html
```

Für die Prüfung durch chinesischsprachige Einkaufsmitarbeiter.  
用于采购人员阅读和人工复核。

### Deutscher HTML-Bericht / 德文 HTML

```text
AB_Check_Report_DE.html
```

Für interne deutschsprachige Kommunikation oder zur Vorbereitung einer Lieferantenklärung.  
可用于内部德文沟通或与供应商澄清前的检查。

> Berichte sind grundsätzlich mit demselben Schutzniveau wie die ursprünglichen Bestell-PDFs zu behandeln.  
> 报告可能包含公司敏感数据。打开、转发和保存报告时，应按照与原始订单 PDF 相同的保护等级处理。

---

## 11. Status und Exit-Codes / 状态和退出码

### Prüfstatus / 检查状态

- `OK`: Die automatische Prüfung ist konsistent. / 自动检查一致。
- `ERROR`: Es liegt eine eindeutige Abweichung vor oder ein Pflichtinhalt fehlt. / 发现明确不一致或缺少必需内容。
- `WARNING`: Ein Wert konnte nicht extrahiert oder nur unscharf verglichen werden. / 未提取到值，或只能进行宽松比较。
- `REVIEW`: Eine manuelle Prüfung ist erforderlich, beispielsweise bei Zahlungsbedingungen oder Lieferadresse. / 必须人工审核，例如付款条件和送货地址。

### Gesamtbewertung / 总体结论

- `Nicht korrekt / Lieferantenklärung erforderlich` beziehungsweise `不正确/需供应商澄清`: mindestens ein `ERROR`.
- `Manuelle Prüfung erforderlich` beziehungsweise `需人工复核`: kein `ERROR`, aber mindestens ein `WARNING` oder `REVIEW`.
- `Korrekt` beziehungsweise `正确`: alle automatischen Prüfungen bestanden und keine offenen Prüfpunkte.

Da Zahlungsbedingungen und Lieferadresse derzeit grundsätzlich den Status `REVIEW` erhalten, lautet das Ergebnis in der Praxis normalerweise mindestens „Manuelle Prüfung erforderlich“.

由于付款条件和送货地址目前固定为 `REVIEW`，实际报告通常至少会显示“需人工复核”。

### Programm-Exit-Codes / 程序退出码

- `0`: Kein `ERROR`. / 没有 `ERROR`。
- `2`: Mindestens ein `ERROR` oder fehlerhafte Befehlszeilenparameter. / 至少存在一个 `ERROR`，或命令行参数检查失败。
- Andere Werte ungleich null: Laufzeitfehler, etwa fehlende Abhängigkeit, beschädigte PDF oder OCR-Fehler. / 运行异常，例如依赖缺失、PDF 损坏或 OCR 执行失败。

Automatisierte Abläufe können anhand des Exit-Codes feststellen, ob ein eindeutiger Fehler vorliegt.  
在自动化流程中，可以根据退出码判断是否存在明确错误。

#### Windows PowerShell

```powershell
python ab_bestellunterlagen_checker_v3.py BESTELLUNG.pdf AB.pdf -o AB_Check_Report
$LASTEXITCODE
```

#### macOS oder Linux / macOS 或 Linux

```bash
python ab_bestellunterlagen_checker_v3.py BESTELLUNG.pdf AB.pdf -o AB_Check_Report
echo $?
```

---

## 12. Manuelle Prüfliste / 人工复核清单

Auch wenn kein `ERROR` gemeldet wird, sind folgende Punkte manuell zu kontrollieren:

即使自动结果没有 `ERROR`，仍建议逐项确认：

1. Stimmt der endgültige SAP-Bestellpreis mit der AB überein?  
   SAP 中的最终订单价格是否与 AB 一致。
2. Enthalten die Zahlungsbedingungen neue Einschränkungen wie `vor Zulassung`, Vorauszahlung oder Ähnliches?  
   付款条件是否新增 `vor Zulassung`、预付款或其他限制。
3. Sind Firmenname, Straße, Postleitzahl, Ort und `Tor` korrekt?  
   公司名称、街道、邮编、城市和 `Tor` 信息是否正确。
4. Stimmen Monat, Kalenderwoche, Jahr sowie die Bedeutung von „voraussichtlich“ oder „unverbindlich“ beim Liefertermin überein?  
   交期的月份、周次、年份和“预计/不具约束力”等语义是否一致。
5. Ist die `Ohne`-Beschreibung tatsächlich von der internen Regel „fehlender Code darf ignoriert werden“ erfasst?  
   Code 描述中的 `Ohne` 是否确实适用于“缺失可忽略”的业务规则。
6. Sind zusätzliche Codes in der AB plausibel, und verändern sie Kosten oder Konfiguration?  
   AB 中额外 Code 是否合理，是否会增加成本或改变配置。
7. Hat OCR möglicherweise `O` und `0` oder `I` und `1` verwechselt?  
   扫描件或 OCR 是否把字母 `O`、数字 `0`、字母 `I`、数字 `1` 混淆。
8. Enthält eine Datei mehrere Fahrzeuge, Versionen oder Preise, von denen möglicherweise nur der erste Treffer extrahiert wurde?  
   多车辆、多版本或多价格文件是否被脚本错误地只提取了第一个匹配值。
9. Wurde in der Lasttabelle die richtige Spalte verglichen, etwa Landeszulassungswert, technischer Wert oder „Technical Load Plus“?  
   载荷表中的“国家许可值”“技术值”和“Technical Load Plus”列是否比较了正确的一列。

---

## 13. `.gitignore` und Datenschutz / 隐私保护配置

Legen Sie im Projektstamm mindestens folgende `.gitignore` an:  
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

`.gitignore` schützt nur Dateien, die noch nicht von Git verfolgt werden. Bereits übertragene Dateien werden dadurch nicht aus der Historie entfernt.

注意：`.gitignore` 只能阻止尚未被 Git 跟踪的文件。若敏感文件已经提交过，单纯添加 `.gitignore` 不会将其从历史记录中删除。

Vor einem Commit prüfen / 检查 Git 即将提交的内容：

```bash
git status
```

Datei aus dem Staging-Bereich entfernen, wenn sie noch nicht committet wurde:  
如果 PDF 或报告已被加入暂存区，但尚未提交：

```bash
git restore --staged path/to/sensitive-file.pdf
```

Verfolgung beenden, Datei aber lokal behalten:  
如果文件已经被 Git 跟踪，但希望今后停止跟踪，同时保留本地文件：

```bash
git rm --cached path/to/sensitive-file.pdf
```

Wenn vertrauliche Informationen bereits in ein Remote-Repository übertragen wurden:

如果敏感信息已推送到远程仓库，应立即：

1. Repository nicht weiter freigeben. / 停止继续分享仓库。
2. IT, Informationssicherheit oder Datenschutzverantwortliche informieren. / 通知公司 IT、信息安全或数据保护负责人。
3. Git-Historie und Remote-Kopien gemäß Unternehmensprozess bereinigen. / 按公司流程清理 Git 历史和远程副本。
4. Zugangsdaten, Tokens oder Passwörter sofort sperren und erneuern. / 如泄露内容包含账号、访问令牌或密码，立即撤销并轮换。

Das Löschen nur des neuesten Commits reicht nicht aus, da die Datei weiterhin in der Git-Historie enthalten sein kann.  
不要只删除最新提交，因为敏感文件可能仍保留在 Git 历史中。

---

## 14. Hinweise zum Quellcode / 源代码保存注意事项

Beim Kopieren aus Chats oder Webseiten können Python-Operatoren als HTML-Entitäten erscheinen, zum Beispiel:

聊天工具或网页复制代码时，可能把 Python 运算符转义为 HTML 实体，例如：

```text
&lt;    kann als &amp;lt; erscheinen / 可能被显示为 &amp;lt;
&gt;    kann als &amp;gt; erscheinen / 可能被显示为 &amp;gt;
```

Im Python-Code müssen echte Operatoren stehen:  
Python 文件中必须保存为真实运算符：

```python
if visible >= 200:
    return pages
```

Nicht / 而不能保存为：

```python
if visible &gt;= 200:
    return pages
```

Nach dem Speichern Syntax prüfen / 保存脚本后，先进行语法检查：

```bash
python -m py_compile ab_bestellunterlagen_checker_v3.py
```

Keine Ausgabe bedeutet normalerweise, dass die Syntaxprüfung erfolgreich war.  
如果没有输出，通常表示语法检查通过。

---

## 15. Häufige Probleme / 常见问题

### `pypdf` fehlt / 提示缺少 `pypdf`

```text
缺少 pypdf。请安装: pip install pypdf
```

Stellen Sie sicher, dass die virtuelle Umgebung aktiv ist, und führen Sie Folgendes aus:  
请确认虚拟环境已激活，然后运行：

```bash
python -m pip install pypdf
```

### PDF enthält nahezu keinen extrahierbaren Text / PDF 几乎没有可提取文本

Häufig handelt es sich um einen Scan. Mögliche Lösungen:  
原因通常是 PDF 为扫描件。可选择：

- OCRmyPDF und Tesseract lokal installieren. / 在本机安装 OCRmyPDF 和 Tesseract。
- Die Datei mit freigegebener Unternehmenssoftware in eine durchsuchbare PDF umwandeln. / 由公司批准的软件将其转换为可搜索 PDF。
- Datei manuell prüfen. / 人工检查文件。

Unternehmensdateien dürfen nicht in Online-OCR-Dienste hochgeladen werden.  
不要将公司文件上传到在线 OCR 服务。

### OCR installiert, Befehl nicht gefunden / OCR 已安装但命令找不到

```bash
ocrmypdf --version
tesseract --version
```

Wenn die Befehle nicht verfügbar sind, sollte die IT Installationspfad und `PATH` prüfen.  
如果命令不存在，请联系 IT 检查安装路径和 `PATH` 环境变量。

### Betrag oder Feld falsch extrahiert / 金额或字段提取错误

Mögliche Ursachen / 可能原因：

- Besonderes Tabellenlayout / PDF 表格布局特殊
- Ungewöhnlich eingebettete Schriftarten / 字体嵌入方式异常
- Mehrere Beträge in einer Datei / 一个文件中存在多个金额
- OCR-Zahlenerkennungsfehler / OCR 把数字识别错误
- Feldbezeichnung passt nicht zum regulären Ausdruck / 字段名称与正则表达式不匹配

Prüfen Sie zuerst die extrahierten Rohwerte im HTML-Bericht und vergleichen Sie sie manuell mit der PDF. Eine Lieferantenklärung darf nicht allein aufgrund des Gesamtstatus versendet werden.

建议先查看 HTML 报告中的原始提取值，再对照 PDF 人工核验。不要仅根据总体状态向供应商发出澄清。

### Code falsch erkannt / Code 被错误识别

Die aktuelle Code-Regel erkennt hauptsächlich folgende Formate:  
当前 Code 规则主要识别以下格式：

```text
0P...
DE...
ZLS..
ZS...
ZF...
```

Bei neuen Codeformaten muss `CODE_RE` angepasst und mit anonymisierten Testdateien regressionsgeprüft werden.  
如果供应商使用新的 Code 格式，需要更新脚本中的 `CODE_RE`，并使用脱敏测试文件回归验证。

### HTML-Bericht lässt sich nicht öffnen / HTML 报告打不开

Die HTML-Dateien sind lokale Dateien und können mit Edge, Chrome oder Firefox geöffnet werden. Laden Sie sie nicht auf Online-HTML-Viewer hoch.

HTML 是本地文件，可以用 Edge、Chrome 或 Firefox 打开。不要将报告上传到在线 HTML 预览网站。

---

## 16. Sicher testen / 安全测试方式

Verwenden Sie für Entwicklung und Tests künstliche oder vollständig anonymisierte Daten:

开发和测试时，请使用人工构造或彻底脱敏的数据：

- Bestellnummer / 订单号：`TEST-001`
- Angebotsnummer / 报价号：`ANGEBOT-TEST`
- Firma / 公司名：`Musterfirma GmbH`
- Adresse / 地址：通用测试地址 / neutrale Testadresse
- Ansprechpartner / 联系人：虚构名称 / erfundener Name
- Betrag / 金额：非真实测试金额 / nicht realer Testbetrag

Eine sichtbare Schwärzung allein reicht bei PDFs nicht aus. Textschichten, Kommentare, Anhänge und Metadaten können vertrauliche Inhalte weiterhin enthalten. Vor einer externen Weitergabe muss ein freigegebenes Anonymisierungswerkzeug verwendet und der extrahierte Text erneut kontrolliert werden.

脱敏时不要只遮住 PDF 可见区域。PDF 中可能仍保留文本层、批注、附件和元数据。对外分享测试文件前，应使用公司批准的脱敏工具，并再次提取文本确认原信息已真正删除。

---

## 17. Bekannte Einschränkungen / 已知限制

- Kein direkter Zugriff auf SAP und keine SAP-Datenprüfung. / 无法直接访问或核对 SAP 中的数据。
- Reguläre Ausdrücke hängen von aktuellen MAN-/Daimler-Dokumentformaten ab. Vorlagenänderungen können Anpassungen erforderlich machen. / 正则表达式依赖当前 MAN/Daimler 文档格式，模板升级后可能需要调整。
- OCR kann Zeichen, Beträge und Codes falsch erkennen. / OCR 可能误识别字符、金额和 Code。
- Bei mehreren Bestellungen, Fahrzeugen oder Versionen in einer PDF wird möglicherweise nur der erste Treffer extrahiert. / 同一 PDF 中包含多个订单、车辆或版本时，部分字段可能只提取第一个匹配值。
- Zahlungsbedingungen, Lieferadressen und Liefertermine können semantisch gleich, aber textlich unterschiedlich sein. / 付款条件、送货地址和交期可能存在语义相同但文本不同的情况。
- Die `Ohne`-Bewertung basiert auf der Beschreibung in der Nähe des Codes. Komplexe Zeilenumbrüche können zu Fehlbewertungen führen. / `Ohne` 判断基于 Code 附近的描述，复杂换行可能导致误判。
- Zusätzliche AB-Codes werden nicht automatisch als Fehler bewertet, können aber Preis, Termin oder Fahrzeugspezifikation verändern und müssen stichprobenartig geprüft werden. / AB 中额外 Code 不自动判错，但额外配置可能影响价格、交期或车辆规格，必须抽查。

---

## 18. Schnellstart / 最小快速开始

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install pypdf
python -m py_compile ab_bestellunterlagen_checker_v3.py
python ab_bestellunterlagen_checker_v3.py private_input\BESTELLUNG.pdf private_input\AB.pdf -o AB_Check_Report
```

### macOS oder Linux / macOS 或 Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install pypdf
python -m py_compile ab_bestellunterlagen_checker_v3.py
python ab_bestellunterlagen_checker_v3.py private_input/BESTELLUNG.pdf private_input/AB.pdf -o AB_Check_Report
```

Öffnen Sie danach zuerst / 运行完成后，优先打开：

```text
AB_Check_Report_ZH.html
```

Prüfen Sie anschließend alle Positionen mit `ERROR`, `WARNING` und `REVIEW` manuell.  
然后对所有 `ERROR`、`WARNING` 和 `REVIEW` 项进行人工核验。

---

## 19. Haftungsausschluss / 责任说明

Dieses Werkzeug ist ausschließlich ein internes Hilfsmittel. Es stellt keine endgültige Bestätigung von Bestellung, Vertrag, Preis, Liefertermin oder technischer Konfiguration dar. Die Bewertung „Korrekt“ bedeutet lediglich, dass innerhalb des extrahierbaren Textes und der implementierten Regeln keine Abweichung erkannt wurde. Die endgültige Freigabe, Lieferantenklärung und SAP-Bearbeitung müssen durch entsprechend berechtigte Personen gemäß den Unternehmensprozessen erfolgen.

本工具是内部辅助检查工具，不构成对订单、合同、价格、交期或技术配置的最终确认。自动报告中的“正确”仅表示脚本在可提取文本和既定规则范围内未发现差异。最终放单、供应商澄清和 SAP 操作仍应由具有相应权限的人员按照公司流程完成。
