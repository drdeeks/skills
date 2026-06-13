# Template

Template and style files for CoLM 2025
# AAAI 2026 统一LaTeX模板使用说明 / AAAI 2026 Unified LaTeX Template Guide

> **📝 重要说明 / Important Notice**: 本仓库借助Cursor在AAAI 2026官方模板基础上改进得到。如果遇到不满足或有冲突的情况，请积极提issues。
> 
> **📝 Important Notice**: This repository is improved based on the official AAAI 2026 template with the assistance of Cursor. If you encounter any issues or conflicts, please actively submit issues.

[中文](#中文版本) | [English](#english-version)

---

## 🌐 在线查看 / Online Access

**📖 在线阅读和测试模板**: [https://cn.overleaf.com/read/wyhcnvcrtpyt#cd4a07](https://cn.overleaf.com/read/wyhcnvcrtpyt#cd4a07)

**📖 Online View and Test Template**: [https://cn.overleaf.com/read/wyhcnvcrtpyt#cd4a07](https://cn.overleaf.com/read/wyhcnvcrtpyt#cd4a07)

💡 **提示 / Tips**: 
- 中文：您可以通过上述链接在Overleaf中直接查看、编辑和编译模板，无需本地安装LaTeX环境
- English: You can view, edit, and compile the template directly in Overleaf using the link above, without needing a local LaTeX installation

---

## 中文版本

### 概述 ✅

我已经将AAAI 2026的两个版本（匿名投稿版本和camera-ready版本）**完整合并**成一个统一的模板文件 `aaai2026-unified-template.tex`。

该模板包含了原始两个模板的**所有完整内容**（共886行，比原始文件更全面），包括：
- 所有格式化说明和要求
- 完整的示例代码和表格
- 图片处理指南
- 参考文献格式要求
- 所有章节和附录内容
- 版本特定的Acknowledgments部分

### 主要差异分析

通过比较原始的两个模板，我发现主要差异在于：

#### 1. 包的加载方式
- **匿名版本**: `\usepackage[submission]{aaai2026}`
- **Camera-ready版本**: `\usepackage{aaai2026}`

#### 2. 标题差异
- **匿名版本**: "AAAI Press Anonymous Submission Instructions for Authors Using LaTeX"
- **Camera-ready版本**: "AAAI Press Formatting Instructions for Authors Using LaTeX --- A Guide"

#### 3. Links环境的处理
- **匿名版本**: Links环境被注释掉，防止泄露作者身份
- **Camera-ready版本**: Links环境正常显示

#### 4. 内容部分差异
- **匿名版本**: 包含"Preparing an Anonymous Submission"部分的特殊说明
- **Camera-ready版本**: 包含完整的格式说明和版权信息

### 依赖文件检查结果

✅ **已验证并复制到主目录的文件**：

- `aaai2026.sty` - AAAI 2026 样式文件（两个版本完全相同）
- `aaai2026.bst` - 参考文献样式文件（两个版本完全相同）
- `aaai2026.bib` - 示例参考文献文件
- `figure1.pdf` 和 `figure2.pdf` - 示例图片文件

所有这些文件在两个版本中都是相同的，因此统一模板可以正常工作。

### 如何使用统一模板

#### 切换到匿名投稿版本
在模板文件第11行，**取消注释**这一行：
```latex
\def\aaaianonymous{true}
```

#### 切换到Camera-ready版本
在模板文件第11行，**注释掉**或**删除**这一行：
```latex
% \def\aaaianonymous{true}
```

### 一键切换的核心机制

统一模板使用了LaTeX的条件编译功能：

```latex
% 条件包加载
\ifdefined\aaaianonymous
    \usepackage[submission]{aaai2026}  % 匿名版本
\else
    \usepackage{aaai2026}              % Camera-ready版本
\fi

% 条件标题设置
\ifdefined\aaaianonymous
    \title{AAAI Press Anonymous Submission\\Instructions for Authors Using \LaTeX{}}
\else
    \title{AAAI Press Formatting Instructions \\for Authors Using \LaTeX{} --- A Guide}
\fi

% 条件内容显示
\ifdefined\aaaianonymous
    % 匿名版本特有内容
\else
    % Camera-ready版本特有内容
\fi
```

### 文件清单

主目录现在包含以下文件：

- `aaai2026-unified-template.tex` - 统一主论文模板文件
- `aaai2026-unified-supp.tex` - 统一补充材料模板文件
- `aaai2026.sty` - AAAI 2026 LaTeX 样式文件
- `aaai2026.bst` - 参考文献样式文件  
- `aaai2026.bib` - 示例参考文献文件
- `figure1.pdf` - 示例图片1
- `figure2.pdf` - 示例图片2
- `README.md` - 本说明文档

### 补充材料模板 (Supplementary Material Template)

#### 概述
`aaai2026-unified-supp.tex` 是专门为AAAI 2026补充材料设计的统一模板，与主论文模板使用相同的版本切换机制。

#### 主要功能
- **版本切换**: 通过修改一行代码在匿名投稿和camera-ready版本间切换
- **补充内容支持**: 支持额外的实验、推导、数据、图表、算法等
- **格式一致性**: 与主论文模板保持完全一致的格式要求
- **代码示例**: 包含算法、代码列表等补充材料的示例

#### 使用方法
与主论文模板相同，只需修改第11行：
```latex
% 匿名投稿版本
\def\aaaianonymous{true}

% Camera-ready版本  
% \def\aaaianonymous{true}
```

#### 补充材料内容建议
- 额外的实验结果和消融研究
- 详细的数学推导和证明
- 更多的图表和可视化
- 算法伪代码和实现细节
- 数据集描述和预处理步骤
- 超参数设置和实验配置
- 失败案例分析
- 计算复杂度分析

### 使用检查清单 (Usage Checklist)

#### 📋 投稿前检查清单 (Pre-Submission Checklist)

**版本设置**:
- [ ] 已设置 `\def\aaaianonymous{true}` (匿名投稿)
- [ ] 已注释掉所有可能暴露身份的信息
- [ ] 已匿名化参考文献（移除作者姓名）

**内容完整性**:
- [ ] 标题、摘要、关键词已填写
- [ ] 所有章节内容完整
- [ ] 图表编号连续且正确
- [ ] 参考文献格式正确
- [ ] 补充材料（如有）已准备

**格式检查**:
- [ ] 页面边距符合要求
- [ ] 字体和字号正确
- [ ] 行间距符合标准
- [ ] 图表位置和大小合适
- [ ] 数学公式格式正确

**技术检查**:
- [ ] LaTeX编译无错误
- [ ] 参考文献正确生成
- [ ] PDF输出正常
- [ ] 文件大小在限制范围内

#### 📋 录用后检查清单 (Post-Acceptance Checklist)

**版本切换**:
- [ ] 已注释掉 `\def\aaaianonymous{true}` (camera-ready)
- [ ] 已添加完整的作者信息
- [ ] 已添加所有作者单位信息
- [ ] 已恢复所有被注释的内容

**内容更新**:
- [ ] 已根据审稿意见修改内容
- [ ] 已更新所有图表和实验
- [ ] 已完善补充材料
- [ ] 已检查所有链接和引用

**最终检查**:
- [ ] 最终PDF质量检查
- [ ] 所有文件已备份
- [ ] 符合会议最终提交要求
- [ ] 补充材料已单独提交（如需要）

#### 📋 补充材料检查清单 (Supplementary Material Checklist)

**内容组织**:
- [ ] 补充材料与主论文内容对应
- [ ] 章节结构清晰合理
- [ ] 图表编号与主论文不冲突
- [ ] 参考文献格式一致

**技术细节**:
- [ ] 算法伪代码清晰完整
- [ ] 实验设置详细说明
- [ ] 数据预处理步骤明确
- [ ] 超参数配置完整

**格式要求**:
- [ ] 使用统一的supp模板
- [ ] 页面设置与主论文一致
- [ ] 字体和格式符合要求
- [ ] 文件大小在限制范围内

### 实际使用建议

1. **投稿阶段**: 
   - 取消注释 `\def\aaaianonymous{true}` 
   - 确保不包含任何可能暴露身份的信息
   - 检查参考文献是否已匿名化

2. **录用后准备final版本**:
   - 注释掉或删除 `\def\aaaianonymous{true}` 这一行
   - 添加完整的作者信息和affiliations
   - 取消注释links环境（如果需要）

3. **编译测试**:
   - 分别在两种模式下编译，确保都能正常工作
   - 检查输出的PDF是否符合要求
   - 验证参考文献格式是否正确

4. **依赖文件确认**:
   - 确保所有依赖文件都在同一目录下
   - 如果移动模板文件，记得同时移动依赖文件

### 重要注意事项

⚠️ **关于Bibliography Style**:
- `aaai2026.sty`文件已经自动设置了`\bibliographystyle{aaai2026}`
- **不要**在文档中再次添加`\bibliographystyle{aaai2026}`命令
- 否则会出现"`Illegal, another \bibstyle command`"错误
- 只需要使用`\bibliography{aaai2026}`命令即可

### 编译命令示例

```bash
# 编译LaTeX文档
pdflatex aaai2026-unified-template.tex
bibtex aaai2026-unified-template
pdflatex aaai2026-unified-template.tex
pdflatex aaai2026-unified-template.tex
```

### 常见问题解决

#### 1. "Illegal, another \bibstyle command"错误
**原因**: 重复设置了bibliography style  
**解决方案**: 删除文档中的`\bibliographystyle{aaai2026}`命令，`aaai2026.sty`会自动处理

#### 2. 参考文献格式不正确
**原因**: 可能缺少natbib包或者BibTeX文件问题  
**解决方案**: 确保按照标准的LaTeX编译流程：pdflatex → bibtex → pdflatex → pdflatex

---

## English Version

### Overview ✅

I have **completely merged** the two AAAI 2026 versions (anonymous submission and camera-ready) into a single unified template file `aaai2026-unified-template.tex`.

This template contains **all complete content** from both original templates (886 lines total, more comprehensive than the original files), including:
- All formatting instructions and requirements
- Complete example codes and tables
- Image processing guidelines
- Reference formatting requirements
- All sections and appendix content
- Version-specific Acknowledgments sections

### Key Differences Analysis

By comparing the two original templates, the main differences are:

#### 1. Package Loading Method
- **Anonymous version**: `\usepackage[submission]{aaai2026}`
- **Camera-ready version**: `\usepackage{aaai2026}`

#### 2. Title Differences
- **Anonymous version**: "AAAI Press Anonymous Submission Instructions for Authors Using LaTeX"
- **Camera-ready version**: "AAAI Press Formatting Instructions for Authors Using LaTeX --- A Guide"

#### 3. Links Environment Handling
- **Anonymous version**: Links environment commented out to prevent identity disclosure
- **Camera-ready version**: Links environment displayed normally

#### 4. Content Section Differences
- **Anonymous version**: Contains special instructions in "Preparing an Anonymous Submission" section
- **Camera-ready version**: Contains complete formatting instructions and copyright information

### Dependency Files Verification

✅ **Files verified and copied to main directory**:

- `aaai2026.sty` - AAAI 2026 style file (identical in both versions)
- `aaai2026.bst` - Bibliography style file (identical in both versions)
- `aaai2026.bib` - Sample bibliography file
- `figure1.pdf` and `figure2.pdf` - Sample image files

All these files are identical in both versions, so the unified template works properly.

### How to Use the Unified Template

#### Switch to Anonymous Submission Version
On line 11 of the template file, **uncomment** this line:
```latex
\def\aaaianonymous{true}
```

#### Switch to Camera-ready Version
On line 11 of the template file, **comment out** or **delete** this line:
```latex
% \def\aaaianonymous{true}
```

### Core Mechanism of One-Click Switching

The unified template uses LaTeX conditional compilation:

```latex
% Conditional package loading
\ifdefined\aaaianonymous
    \usepackage[submission]{aaai2026}  % Anonymous version
\else
    \usepackage{aaai2026}              % Camera-ready version
\fi

% Conditional title setting
\ifdefined\aaaianonymous
    \title{AAAI Press Anonymous Submission\\Instructions for Authors Using \LaTeX{}}
\else
    \title{AAAI Press Formatting Instructions \\for Authors Using \LaTeX{} --- A Guide}
\fi

% Conditional content display
\ifdefined\aaaianonymous
    % Anonymous version specific content
\else
    % Camera-ready version specific content
\fi
```

### File List

The main directory now contains the following files:

- `aaai2026-unified-template.tex` - Unified main paper template file
- `aaai2026-unified-supp.tex` - Unified supplementary material template file
- `aaai2026.sty` - AAAI 2026 LaTeX style file
- `aaai2026.bst` - Bibliography style file
- `aaai2026.bib` - Sample bibliography file
- `figure1.pdf` - Sample image 1
- `figure2.pdf` - Sample image 2
- `README.md` - This documentation

### Supplementary Material Template

#### Overview
`aaai2026-unified-supp.tex` is a unified template specifically designed for AAAI 2026 supplementary materials, using the same version switching mechanism as the main paper template.

#### Key Features
- **Version Switching**: Switch between anonymous submission and camera-ready versions by modifying one line of code
- **Supplementary Content Support**: Supports additional experiments, derivations, data, figures, algorithms, etc.
- **Format Consistency**: Maintains complete format consistency with the main paper template
- **Code Examples**: Includes examples for algorithms, code listings, and other supplementary materials

#### Usage
Same as the main paper template, just modify line 11:
```latex
% Anonymous submission version
\def\aaaianonymous{true}

% Camera-ready version
% \def\aaaianonymous{true}
```

#### Supplementary Material Content Suggestions
- Additional experimental results and ablation studies
- Detailed mathematical derivations and proofs
- More figures and visualizations
- Algorithm pseudocode and implementation details
- Dataset descriptions and preprocessing steps
- Hyperparameter settings and experimental configurations
- Failure case analysis
- Computational complexity analysis

### Usage Checklist

#### 📋 Pre-Submission Checklist

**Version Setup**:
- [ ] Set `\def\aaaianonymous{true}` (anonymous submission)
- [ ] Commented out all information that could reveal identity
- [ ] Anonymized references (removed author names)

**Content Completeness**:
- [ ] Title, abstract, and keywords filled
- [ ] All sections complete
- [ ] Figure and table numbers consecutive and correct
- [ ] Reference format correct
- [ ] Supplementary materials prepared (if any)

**Format Check**:
- [ ] Page margins meet requirements
- [ ] Font and font size correct
- [ ] Line spacing meets standards
- [ ] Figure and table positions and sizes appropriate
- [ ] Mathematical formula format correct

**Technical Check**:
- [ ] LaTeX compilation error-free
- [ ] References generated correctly
- [ ] PDF output normal
- [ ] File size within limits

#### 📋 Post-Acceptance Checklist

**Version Switch**:
- [ ] Commented out `\def\aaaianonymous{true}` (camera-ready)
- [ ] Added complete author information
- [ ] Added all author affiliation information
- [ ] Restored all commented content

**Content Updates**:
- [ ] Modified content according to reviewer comments
- [ ] Updated all figures and experiments
- [ ] Completed supplementary materials
- [ ] Checked all links and citations

**Final Check**:
- [ ] Final PDF quality check
- [ ] All files backed up
- [ ] Meets conference final submission requirements
- [ ] Supplementary materials submitted separately (if needed)

#### 📋 Supplementary Material Checklist

**Content Organization**:
- [ ] Supplementary materials correspond to main paper content
- [ ] Chapter structure clear and reasonable
- [ ] Figure and table numbers don't conflict with main paper
- [ ] Reference format consistent

**Technical Details**:
- [ ] Algorithm pseudocode clear and complete
- [ ] Experimental setup explained in detail
- [ ] Data preprocessing steps clear
- [ ] Hyperparameter configuration complete

**Format Requirements**:
- [ ] Using unified supp template
- [ ] Page settings consistent with main paper
- [ ] Font and format meet requirements
- [ ] File size within limits

### Practical Usage Recommendations

1. **Submission Stage**: 
   - Uncomment `\def\aaaianonymous{true}` 
   - Ensure no information that could reveal identity is included
   - Check that references are anonymized

2. **Preparing final version after acceptance**:
   - Comment out or delete the `\def\aaaianonymous{true}` line
   - Add complete author information and affiliations
   - Uncomment links environment (if needed)

3. **Compilation Testing**:
   - Compile in both modes to ensure proper functionality
   - Check if the output PDF meets requirements
   - Verify reference formatting is correct

4. **Dependency File Confirmation**:
   - Ensure all dependency files are in the same directory
   - Remember to move dependency files when moving the template file

### Important Notes

⚠️ **About Bibliography Style**:
- The `aaai2026.sty` file automatically sets `\bibliographystyle{aaai2026}`
- **Do NOT** add `\bibliographystyle{aaai2026}` command again in your document
- Otherwise you'll get "`Illegal, another \bibstyle command`" error
- Just use the `\bibliography{aaai2026}` command

### Compilation Commands Example

```bash
# Compile LaTeX document
pdflatex aaai2026-unified-template.tex
bibtex aaai2026-unified-template
pdflatex aaai2026-unified-template.tex
pdflatex aaai2026-unified-template.tex
```

### Common Issues and Solutions

#### 1. "Illegal, another \bibstyle command" Error
**Cause**: Duplicate bibliography style setting  
**Solution**: Remove the `\bibliographystyle{aaai2026}` command from your document, `aaai2026.sty` handles it automatically

#### 2. Incorrect Reference Format
**Cause**: Missing natbib package or BibTeX file issues  
**Solution**: Follow the standard LaTeX compilation process: pdflatex → bibtex → pdflatex → pdflatex

---

## 版本信息 / Version Information

- **模板版本 / Template Version**: AAAI 2026 Unified (Main + Supplementary)
- **创建日期 / Created**: 2024年12月
- **支持格式 / Supported Formats**: Anonymous Submission & Camera-Ready
- **模板类型 / Template Types**: Main Paper Template & Supplementary Material Template
- **兼容性 / Compatibility**: LaTeX 2020+ / TeXLive 2024+

---

🎉 **现在您只需要修改一行代码就可以在两个版本之间切换，同时所有必要的依赖文件都已经准备就绪！**  
🎉 **Now you only need to modify one line of code to switch between the two versions, with all necessary dependency files ready to use!**# *ACL Paper Styles

This directory contains the latest LaTeX templates for *ACL conferences.

## Instructions for authors

Paper submissions to *ACL conferences must use the official ACL style
templates.

The LaTeX style files are available

- as an [Overleaf template](https://www.overleaf.com/latex/templates/association-for-computational-linguistics-acl-conference/jvxskxpnznfj)
- in this repository
- as a [.zip file](https://github.com/acl-org/acl-style-files/archive/refs/heads/master.zip)

Please see [`acl_latex.tex`](https://github.com/acl-org/acl-style-files/blob/master/acl_latex.tex) for an example.

Please follow the paper formatting guidelines general to *ACL
conferences:

- [Paper formatting guidelines](https://acl-org.github.io/ACLPUB/formatting.html)

Authors may not modify these style files or use templates designed for
other conferences.

## Instructions for publications chairs

To adapt the style files for your conference, please fork this repository and
make necessary changes. Minimally, you'll need to update the name of
the conference and rename the files.

If you make improvements to the templates that should be propagated to
future conferences, please submit a pull request. Thank you in
advance!

In older versions of the templates, authors were asked to fill in the
START submission ID so that it would be stamped at the top of each
page of the anonymized version. This is no longer needed, because it
is now possible to do this stamping automatically within
START. Currently, the way to do this is for the program chair to email
support@softconf.com and request it.

## Instructions for making changes to style files

- merge pull request in github, or push to github
- git pull from github to a local repository
- then, git push from your local repository to overleaf project 
    - Overleaf project is https://www.overleaf.com/project/5f64f1fb97c4c50001b60549
    - Overleaf git url is https://git.overleaf.com/5f64f1fb97c4c50001b60549
- then, click "Submit" and then "Submit as Template" in overleaf in order to ask overleaf to update the overleaf template from the overleaf project 
# Instructions for *ACL Proceedings

The following instructions are for authors of papers submitted for review to ACL conferences (hereafter, "review version") or paper accepted for publication in its proceedings (hereafter, "final version").
All authors are required to adhere to these specifications.

## Style Files

*ACL provides style files for LaTeX and Microsoft Word that meet these requirements. They can be found at:

> https://acl-org.github.io/ACLPUB/

We strongly recommend the use of these style files, which have been appropriately tailored for the *ACL proceedings.

## Paper Length

The conference accepts submissions of long papers and short papers.
Review versions of long papers may have up to eight (8) pages of content plus unlimited pages for references.
Upon acceptance, final versions of long papers will be given one additional page -- up to nine (9) pages of content plus unlimited pages for acknowledgements and references -- so that reviewers' comments can be taken into account.
Review versions of short papers may have up to four (4) pages of content, plus unlimited pages for references.
Final versions of short papers may have up to five (5) pages, plus unlimited pages for acknowledgements and references.
For both long and short papers, all figures and tables that are part of the main text must fit within these page limits.

The conference encourages submission of appendices and supplementary material, which are not required to fit within these page limits. However, review versions of papers must be self-contained: it is optional for reviewers to look at appendices or supplementary material. Please see [Appendices](#Appendices) and [Supplementary](#Supplementary Material) for more information.

Review versions should not refer, for further detail, to documents, code or data resources that are not available to the reviewers.

Papers that do not conform to these requirements may be rejected without review.

Workshop chairs may have different rules for allowed length and whether appendices or supplementary materials are welcome.
As always, the respective call for papers is the authoritative source.

## Anonymity

As reviewing will be double-blind, review versions must not include any identifying information about the authors (such as names, affiliations, or URLs).
Self-references that reveal the author's identity, e.g.,

> We previously showed (Gusfield, 1997)...

must be avoided, and anonymous citations, e.g.,

> We previously showed (Anonymous, 1997)...

should also be avoided. Instead, use citations such as

> Gusfield (1997) previously showed...

Review versions must not include acknowledgements.

**Papers that do not conform to these requirements may be rejected without review.**

Any preliminary non-archival versions of submitted papers should be listed in the submission form but not in the review version of the paper.
Reviewers are generally aware that authors may present preliminary versions of their work in other venues, but will not be provided the list of previous presentations from the submission form.

Once a paper has been accepted to the conference, the final version should include the author's names and affiliations, and is allowed to use self-references.

## Multiple Submission

Papers that have been or will be submitted to other meetings or publications must indicate this at submission time in the START submission form, and must be withdrawn from the other venues if accepted by *ACL.
Authors of papers accepted for presentation at *ACL must notify the program chairs by the deadline for final versions ("camera-ready deadline") whether the paper will be presented.
We will not accept for publication or presentation any papers that overlap significantly in content or results with papers that will be (or have been) published elsewhere.

Authors submitting more than one paper to *ACL must ensure that submissions do not overlap significantly (>25%) with each other in content or results.

## Formatting Instructions

### File Format

Papers must be in Adobe Portable Document Format (PDF).
Please make sure that your PDF file embeds all necessary fonts (especially for tree diagrams, symbols, and Asian languages).
When you print or create the PDF file, there is usually an option in your printer setup to include none, all or just non-standard fonts.
Please make sure that you select the option of including *all* the fonts.
**Before sending it, test your PDF by printing it from a computer different from the one where it was created.**

Some word processors may generate very large PDF files, where each page is rendered as an image.
Such images may reproduce poorly.
In this case, try alternative ways to obtain the PDF.

All papers must use **A4 paper format** (21 cm x 29.7 cm).
Papers must not be submitted with any other paper size.

If you cannot meet the above requirements, please contact the publication chairs as soon as possible.

### Layout

All text except for page numbers must fit within the margins.

Review versions should have page numbers, centered in the bottom margin, but **pages should not be numbered in the final version.**

Manuscripts must be set in two columns.
Exceptions to the two-column format include the title, authors' names and complete addresses, which must be centered at the top of the first page, and any full-width figures or tables.

The exact dimensions for a page on A4 paper are:

* Left margin: 2.5 cm
* Right margin: 2.5 cm
* Top margin: 2.5 cm
* Bottom margin: 2.5 cm
* Column width: 7.7 cm
* Column height: 24.7 cm
* Gap between columns: 0.6 cm

In the review version, a ruler (line numbers in the left and right margins of the article) should be printed, so that reviewers may comment on particular lines in the paper.
The ruler should not change the appearance of any other content on the page.
The final version should not contain a ruler.

### Fonts

All text (except non-Latin scripts and mathematical formulas) should be set in **Times Roman**.
If Times Roman is unavailable, you may use **Times New Roman** or **Computer Modern Roman.**

The following table specifies what font sizes and styles must be used for each type of text in the manuscript.

| Type of Text          | Font Size | Style |
| --------------------- | --------- | ----- |
| paper title           | 15 pt     | bold  |
| author names          | 12 pt     | bold  |
| author affiliation    | 12 pt     |       |
| the word ``Abstract'' | 12 pt     | bold  |
| section titles        | 12 pt     | bold  |
| subsection titles     | 11 pt     | bold  |
| document text         | 11 pt     |       |
| captions              | 10 pt     |       |
| abstract text         | 10 pt     |       |
| bibliography          | 10 pt     |       |
| footnotes             | 9 pt      |       |

### Title and Authors

Center the title, author's name(s) and affiliation(s) across both columns.

Place the title centered at the top of the first page, in 15-point bold.
Long titles should be typed on two lines without a blank line intervening.
Put the title 2.5 cm from the top of the page.
Write the title in [title case](https://apastyle.apa.org/style-grammar-guidelines/capitalization/title-case); do not write the title in all capital letters, except for acronyms (e.g., "BLEU") or proper nouns ("English") that are normally uppercased or capitalized.

Place the author name(s) and affiliation(s) under the title.
Write authors' full names; do not abbreviate given names to initials, unless they are normally written as initials ("Margaret Mitchell", not "M. Mitchell").
Do not format surnames in all capitals ("Mitchell", not "MITCHELL").

Do not use footnotes for affiliations.
The affiliation should contain the author's complete address, and if possible, an electronic mail address.

The title, author names and addresses should be completely identical to those entered to the paper submission website in order to maintain the consistency of author information among all publications of the conference.
If they are different, the publication chairs may resolve the difference without consulting with you; so it is in your own interest to double-check that the information is consistent.

Start the body of the first page 7.5 cm from the top of the page.
**Even in the review version of the paper, you should maintain space for names and addresses so that they will fit in the final version.**

### Abstract

Type the abstract at the beginning of the first column.
Center the word **Abstract** in 12 point bold above the body of the abstract.
The width of the abstract should be smaller than the
normal column width by 0.6 cm on each side.
The abstract text should be 10 point roman, single-spaced.

The abstract should be a concise summary of the general thesis and conclusions of the paper.
It should be no longer than 200 words.

### Text

Begin typing the main body of the text immediately after the abstract, continuing in two columns.
The text should be 11 point roman, single-spaced.

Indent 0.4 cm when starting a new paragraph, except for the first paragraph in a section.

### Sections

Use numbered sections (Arabic numerals) to facilitate cross references.
Number subsections with the section number and the subsection number separated by a dot, in Arabic numerals, e.g.,

> 1 Introduction

or

> 6.1 File Format

### Footnotes
Put footnotes at the bottom of the page and use 9 point font.
They may be numbered or referred to by asterisks or other symbols.
Footnotes should be separated from the text by a line.

### Figures and tables

Place figures and tables in the paper near where they are first discussed, rather than at the end, if possible.
Wide figures/tables may run across both columns.

To accommodate people who are color-blind (as well as those printing with black-and-white printers), grayscale readability is strongly encouraged.
Color is not forbidden, but authors should ensure that tables and figures do not rely solely on color to convey critical distinctions.

**Captions:**
Provide a caption for every figure/table; number each one sequentially in the form:

> Figure 1: Caption of the Figure.

and

> Table 1: Caption of the Table.

Captions should be placed below figures/tables, in 10 point roman type.
Captions that are one line are centered.
Captions longer than one line are left-aligned.

### Hyperlinks

Within-document and external hyperlinks should be dark blue (hex #000099), not underlined or boxed.

### Non-English Text

Text in languages other than English should be accompanied by translations into English, and text in scripts other than Latin should \emph{also} be accompanied by transliterations into Latin script, since not all readers can recognize non-Latin characters easily.

For example, παράδειγμα *paradeigma* ‘example’ is a Greek word, and this is a Greek sentence:

> Αυτό είναι ένα παράδειγμα.  
> auto einai ena paradeigma.  
> ‘This is an example.’

### Citations

Citations within the text appear in parentheses (Gusfield, 1997), or, if the author's name appears in the text itself: Gusfield (1997).
Append lowercase letters to the year in cases of ambiguities.
Cite papers with two authors using both authors' names (Aho and Ullman, 1972), but cite papers with more than two authors by the first author's name and ``et al.'' (Chandra et al., 1981).
Collapse multiple citations into a single pair of parentheses (Gusfield, 1997; Aho and Ullman, 1972).

Refrain from using full citations as sentence constituents.
Instead of

> (Gusfield, 1997) showed that ...  
> In (Gusfield, 1997), ...''

write

> Gusfield (1997) showed that ...  
> In Gusfield (1997), ...

Submissions should accurately reference prior and related work, including code and data.
If a piece of prior work appeared in multiple venues, the version that appeared in a refereed, archival venue should be referenced.
If multiple versions of a piece of prior work exist, the one used by the authors should be referenced.

### Acknowledgments

The acknowledgments should go immediately before the references.
Do not number the acknowledgments section.
Do not include this section in the review version.

### References

Gather the full set of references together under the unnumbered section heading **References**.
Place the References section before any Appendices.
Arrange the references alphabetically by first author, rather than by order of occurrence in the text.

Provide as complete a citation as possible, using a consistent format, such as the [one for Computational Linguistics](http://cljournal.org/style_guide_refs.html) or the one in the [Publication Manual of the American Psychological Association](https://apastyle.apa.org/products/publication-manual-7th-edition).
Use full names for authors, not just initials.
Authors should not rely on automated citation indices to provide accurate references for prior and related work.

As part of our work to make ACL materials more widely used and cited outside of our discipline, ACL has registered as a CrossRef member, as a registrant of Digital Object Identifiers (DOIs), the standard for registering permanent URNs for referencing scholarly materials.

All references are required to contain DOIs of all cited works when possible, or, as a second resort, links to ACL Anthology pages.
Appropriate records should be found for most materials in the current [ACL Anthology](https://aclweb.org/anthology/).

Example article in a journal:

> Rie Kubota Ando and Tong Zhang. 2005. [A framework for learning predictive structures from multiple tasks and unlabeled data](https://www.jmlr.org/papers/v6/ando05a.html). *Journal of Machine Learning Research*, 6:1817–1853.

Example paper in non-ACL proceedings, with DOI:

> Galen Andrew and Jianfeng Gao. 2007. [Scalable training of L1-regularized log-linear models](https://doi.org/10.1145/1273496.1273501). In *Proceedings of the 24th International Conference on Machine Learning*, pages 33–40.

Example ACL Anthology paper with DOI:

> James Goodman, Andreas Vlachos, and Jason Naradowsky. 2016. [Noise reduction and targeted exploration in imitation learning for Abstract Meaning Representation parsing](http://dx.doi.org/10.18653/v1/P16-1001). In *Proceedings of the 54th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)*, pages 1–45711, Berlin, Germany. Association for Computational Linguistics.

Example ACL Anthology paper without DOI:

> Benjamin Börschinger and Mark Johnson. 2011. [A particle filter algorithm for Bayesian word segmentation](https://www.aclweb.org/anthology/U11-1004/). In *Proceedings of the Australasian Language Technology Association Workshop 2011*, pages 10–44718, Canberra, Australia.

Example arXiv paper:

> Mohammad Sadegh Rasooli and Joel R. Tetreault. 2015. [Yara parser: A fast and accurate dependency parser](http://arxiv.org/abs/1503.06733). *Computing Research Repository*, arXiv:1503.06733. Version 2.

## Appendices

Appendices are material that can be read, and include lemmas, formulas, proofs, and tables that are not critical to the reading and understanding of the paper.
Letter them in sequence and provide an informative title:

> Appendix A. Title of Appendix

The appendices come after the references.

Review versions of appendices must follow the same anonymity guidelines as the main paper.

## Supplementary Material

Submissions may include non-readable supplementary material used in the work and described in the paper.
Any accompanying software and/or data should include licenses and documentation of research review as appropriate.
Supplementary material may report preprocessing decisions, model parameters, and other details necessary for the replication of the experiments reported in the paper.
Seemingly small preprocessing decisions can sometimes make a large difference in performance, so it is crucial to record such decisions to precisely characterize state-of-the-art methods.

Nonetheless, supplementary material should be supplementary (rather than central) to the paper.
**Submissions that misuse the supplementary material may be rejected without review.**
Supplementary material may include explanations or details of proofs or derivations that do not fit into the paper, lists of features or feature templates, sample inputs and outputs for a system, pseudo-code or source code, and data.
(Source code and data should be separate uploads, rather than part of the paper).

The paper should not rely on the supplementary material: while the paper may refer to and cite the supplementary material and the supplementary material will be available to the reviewers, they will not be asked to review the supplementary material.

Review versions of supplementary material must follow the same anonymity guidelines as the main paper.

## Credits

This document has been adapted from the instructions for earlier ACL and NAACL proceedings, including those for
ACL 2020 by Steven Bethard, Ryan Cotterell and Rui Yan,
ACL 2019 by Douwe Kiela and Ivan Ivan Vulić,
NAACL 2019 by Stephanie Lukin and Alla Roskovskaya,
ACL 2018 by Shay Cohen, Kevin Gimpel, and Wei Lu,
NAACL 2018 by Margaret Mitchell and Stephanie Lukin,
BibTeX suggestions for (NA)ACL 2017/2018 from Jason Eisner,
ACL 2017 by Dan Gildea and Min-Yen Kan,
NAACL 2017 by Margaret Mitchell,
ACL 2012 by Maggie Li and Michael White,
ACL 2010 by Jing-Shin Chang and Philipp Koehn,
ACL 2008 by Johanna D. Moore, Simone Teufel, James Allan, and Sadaoki Furui,
ACL 2005 by Hwee Tou Ng and Kemal Oflazer,
ACL 2002 by Eugene Charniak and Dekang Lin,
and earlier ACL and EACL formats written by several people, including
John Chen, Henry S. Thompson and Donald Walker.
Additional elements were taken from the formatting instructions of the *International Joint Conference on Artificial Intelligence* and the *Conference on Computer Vision and Pattern Recognition*.
# LaTeX Templates for ML/AI Conferences

This directory contains official LaTeX templates for major machine learning and AI conferences.

---

## Compiling LaTeX to PDF

### Option 1: VS Code with LaTeX Workshop (Recommended)

**Setup:**
1. Install [TeX Live](https://www.tug.org/texlive/) (full distribution recommended)
   - macOS: `brew install --cask mactex`
   - Ubuntu: `sudo apt install texlive-full`
   - Windows: Download from [tug.org/texlive](https://www.tug.org/texlive/)

2. Install VS Code extension: **LaTeX Workshop** by James Yu
   - Open VS Code → Extensions (Cmd/Ctrl+Shift+X) → Search "LaTeX Workshop" → Install

**Usage:**
- Open any `.tex` file in VS Code
- Save the file (Cmd/Ctrl+S) → Auto-compiles to PDF
- Click the green play button or use `Cmd/Ctrl+Alt+B` to build
- View PDF: Click "View LaTeX PDF" icon or `Cmd/Ctrl+Alt+V`
- Side-by-side view: `Cmd/Ctrl+Alt+V` then drag tab

**Settings** (add to VS Code `settings.json`):
```json
{
  "latex-workshop.latex.autoBuild.run": "onSave",
  "latex-workshop.view.pdf.viewer": "tab",
  "latex-workshop.latex.recipes": [
    {
      "name": "pdflatex → bibtex → pdflatex × 2",
      "tools": ["pdflatex", "bibtex", "pdflatex", "pdflatex"]
    }
  ]
}
```

### Option 2: Command Line

```bash
# Basic compilation
pdflatex main.tex

# With bibliography (full workflow)
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex

# Using latexmk (handles dependencies automatically)
latexmk -pdf main.tex

# Continuous compilation (watches for changes)
latexmk -pdf -pvc main.tex
```

### Option 3: Overleaf (Online)

1. Go to [overleaf.com](https://www.overleaf.com)
2. New Project → Upload Project → Upload the template folder as ZIP
3. Edit online with real-time PDF preview
4. No local installation needed

### Option 4: Other IDEs

| IDE | Extension/Plugin | Notes |
|-----|------------------|-------|
| **Cursor** | LaTeX Workshop | Same as VS Code |
| **Sublime Text** | LaTeXTools | Popular, well-maintained |
| **Vim/Neovim** | VimTeX | Powerful, keyboard-driven |
| **Emacs** | AUCTeX | Comprehensive LaTeX environment |
| **TeXstudio** | Built-in | Dedicated LaTeX IDE |
| **Texmaker** | Built-in | Cross-platform LaTeX editor |

### Troubleshooting Compilation

**"File not found" errors:**
```bash
# Ensure you're in the template directory
cd templates/icml2026
pdflatex example_paper.tex
```

**Bibliography not appearing:**
```bash
# Run bibtex after first pdflatex
pdflatex main.tex
bibtex main        # Uses main.aux to find citations
pdflatex main.tex  # Incorporates bibliography
pdflatex main.tex  # Resolves references
```

**Missing packages:**
```bash
# TeX Live package manager
tlmgr install <package-name>

# Or install full distribution to avoid this
```

---

## Available Templates

| Conference | Directory | Year | Source |
|------------|-----------|------|--------|
| ICML | `icml2026/` | 2026 | [Official ICML](https://icml.cc/Conferences/2026/AuthorInstructions) |
| ICLR | `iclr2026/` | 2026 | [Official GitHub](https://github.com/ICLR/Master-Template) |
| NeurIPS | `neurips2025/` | 2025 | Community template |
| ACL | `acl/` | 2025+ | [Official ACL](https://github.com/acl-org/acl-style-files) |
| AAAI | `aaai2026/` | 2026 | [AAAI Author Kit](https://aaai.org/authorkit26/) |
| COLM | `colm2025/` | 2025 | [Official COLM](https://github.com/COLM-org/Template) |

## Usage

### ICML 2026

```latex
\documentclass{article}
\usepackage{icml2026}  % For submission
% \usepackage[accepted]{icml2026}  % For camera-ready

\begin{document}
% Your paper content
\end{document}
```

Key files:
- `icml2026.sty` - Style file
- `icml2026.bst` - Bibliography style
- `example_paper.tex` - Example document

### ICLR 2026

```latex
\documentclass{article}
\usepackage[submission]{iclr2026_conference}  % For submission
% \usepackage[final]{iclr2026_conference}  % For camera-ready

\begin{document}
% Your paper content
\end{document}
```

Key files:
- `iclr2026_conference.sty` - Style file
- `iclr2026_conference.bst` - Bibliography style
- `iclr2026_conference.tex` - Example document

### ACL Venues (ACL, EMNLP, NAACL)

```latex
\documentclass[11pt]{article}
\usepackage[review]{acl}  % For review
% \usepackage{acl}  % For camera-ready

\begin{document}
% Your paper content
\end{document}
```

Key files:
- `acl.sty` - Style file
- `acl_natbib.bst` - Bibliography style
- `acl_latex.tex` - Example document

### AAAI 2026

```latex
\documentclass[letterpaper]{article}
\usepackage[submission]{aaai2026}  % For submission
% \usepackage{aaai2026}  % For camera-ready

\begin{document}
% Your paper content
\end{document}
```

Key files:
- `aaai2026.sty` - Style file
- `aaai2026.bst` - Bibliography style

### COLM 2025

```latex
\documentclass{article}
\usepackage[submission]{colm2025_conference}  % For submission
% \usepackage[final]{colm2025_conference}  % For camera-ready

\begin{document}
% Your paper content
\end{document}
```

Key files:
- `colm2025_conference.sty` - Style file
- `colm2025_conference.bst` - Bibliography style

## Page Limits Summary

| Conference | Submission | Camera-Ready | Notes |
|------------|-----------|--------------|-------|
| ICML 2026 | 8 pages | 9 pages | +unlimited refs/appendix |
| ICLR 2026 | 9 pages | 10 pages | +unlimited refs/appendix |
| NeurIPS 2025 | 9 pages | 9 pages | +checklist outside limit |
| ACL 2025 | 8 pages (long) | varies | +unlimited refs/appendix |
| AAAI 2026 | 7 pages | 8 pages | +unlimited refs/appendix |
| COLM 2025 | 9 pages | 10 pages | +unlimited refs/appendix |

## Common Issues

### Compilation Errors

1. **Missing packages**: Install full TeX distribution (TeX Live Full or MikTeX)
2. **Bibliography errors**: Use the provided `.bst` file with `\bibliographystyle{}`
3. **Font warnings**: Install `cm-super` or use `\usepackage{lmodern}`

### Anonymization

For submission, ensure:
- No author names in `\author{}`
- No acknowledgments section
- No grant numbers
- Use anonymous repositories
- Cite own work in third person

### Common LaTeX Packages

```latex
% Recommended packages (check compatibility with venue style)
\usepackage{amsmath,amsthm,amssymb}  % Math
\usepackage{graphicx}                 % Figures
\usepackage{booktabs}                 % Tables
\usepackage{hyperref}                 % Links
\usepackage{algorithm,algorithmic}    % Algorithms
\usepackage{natbib}                   % Citations
```

## Updating Templates

Templates are updated annually. Check official sources before each submission:

- ICML: https://icml.cc/
- ICLR: https://iclr.cc/
- NeurIPS: https://neurips.cc/
- ACL: https://github.com/acl-org/acl-style-files
- AAAI: https://aaai.org/
- COLM: https://colmweb.org/
