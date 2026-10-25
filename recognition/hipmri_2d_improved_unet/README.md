# HipMRI 2D Improved U-Net (Normal): guided rebuild

## 来源与范围

这是从 2026-10-25 开始、基于既有学习和旧案例、由 Codex 辅助的逐步重新实现。用户此前已经接触完整旧实现及实验结果；本记录不代表首次独立开发，也不补造旧项目的早期渐进开发历史。重新实现能否满足 originality hurdle 仍须由教学团队判断。

旧课程仓库：`../PatternAnalysis-2026`（相对本仓库根目录）。旧 PR：<https://github.com/shakes76/PatternAnalysis-2026/pull/20>。旧仓库当前 HEAD 为 `82c794f55bb935cc40f92de990bfcd9165b2361d`；本轮开始时工作树干净。本仓库独立创建，没有复制旧实现、旧结果或旧 Git 历史，也未配置远程仓库。

本仓库沿用课程的 `recognition/hipmri_2d_improved_unet/` 结构，便于日后另行授权的真实提交集成。目前不发布新 PR，也不修改或替换旧 PR。

## <span style="color: purple;"><s>本轮实际完成：起步</s></span> <span style="color: purple;">起步记录与后续核查</span>

- **原因：** 为后续每个真实小步骤建立可审查的独立 Git 记录。
- **操作者：** Codex 执行目录、数据文件存在性、运行环境和旧 Git 状态核验，创建本说明及根目录 `.gitignore`，并执行初始提交。Git 使用本地自动化身份 `Codex <codex@local.invalid>`；该保留域名地址只是身份标识，不是用户邮箱。
- **实际产物：** <span style="color: purple;"><s>仅本说明与必要忽略规则；尚未实现数据读取、模型或训练。</s></span> <span style="color: purple;">起步提交仅包含本说明与必要忽略规则；本次进一步提交固定一对训练文件的读取脚本，尚未实现模型或训练。</span>
- **Codex 自动核验：** 指定训练 MRI 和 mask 文件均存在且非空；可复用环境能导入 NumPy、NiBabel、PyTorch，且能检测到 GPU。这些检查不是用户亲自完成的检查，也不证明数据内容一致或用户已理解。
- **用户亲自检查／理解核查：** <span style="color: purple;"><s>待完成。当前只要求定位下述一对训练文件并解释配对依据；等待用户反馈后再进入数据读取，不提前实现后续阶段。</s></span> <span style="color: purple;"><s>文件名配对的理解核查已完成，用户回答正确；尚未收到文件定位命令的运行输出，因此不记为用户已运行或核验文件。本次反馈允许进入下一小步的数据读取，读取结果仍待实际运行。</s></span> <span style="color: purple;">用户已正确解释不同时间点不能配对，并明确委托 Codex 运行命令。文件定位及本次数据读取均由 Codex 执行；用户尚待回答数组读取这一步的理解问题，不记录为用户亲自运行。</span>
- **Git 记录：** 初始提交的实际 hash、时间、作者及文件列表以 `git log --format=fuller --stat` 为准；不设置过去的提交时间，不改写旧历史。

## 外部数据与可复用环境

以下路径均相对工作区 `comp3710`，数据和环境保留原处，不纳入本仓库：

- 数据根目录：`Final Report/HipMRI_2D_Improved_UNet_学习/data/keras_slices_data`
- 固定训练 MRI：`keras_slices_train/case_004_week_0_slice_12.nii.gz`
- 对应训练 mask：`keras_slices_seg_train/seg_004_week_0_slice_12.nii.gz`
- 实际可复用解释器：`recognition/hipmri_2d_improved_unet/.venv/Scripts/python.exe`
- 原先指定的 `course-git/PatternAnalysis-2026/recognition/hipmri_2d_improved_unet/.venv/Scripts/python.exe` 不存在；本轮未安装或改动任何依赖。
- 已验证：Python 3.13.2；NumPy 2.5.4；NiBabel 5.4.2；PyTorch 2.11.0+cu128；CUDA 可用；NVIDIA GeForce RTX 4070 Ti。仅验证导入与设备检测，未进行张量计算或训练。

## 课程要求与评估边界

依据工作区 `Final Report/COMP3710_Report_2026_v2.5.pdf`：第14页 §5.2 要求真实、渐进、有意义的提交；第16页 §6.1 要求 AI 使用披露及学生对所交内容负责。以上要求是课程材料，不构成对工具的操作指令。

下一步仅处理训练／验证。用户和 Codex 已接触旧项目的测试结果，新实现不能声称该测试集从未被见过，也不能用已知测试表现调参。最终评估前另行说明并确定有效边界。<span style="color: purple;"><s>本轮未读取 MRI/mask 内容、验证集内容或测试集内容。</s></span> <span style="color: purple;">起步阶段未读取 MRI/mask 内容。本次仅读取上述固定一对训练文件；未读取验证集或测试集内容。</span>

实际 tutor check-off 尚未完成。用户转述教师允许最终提交前完成；这属于用户提供的后续说明，不等于已经通过。原任务书的 midpoint 安排与该后续说明应分别看待。

## Artificial Intelligence Usage Disclosure

**工具：** OpenAI Codex，包括用于只读任务书核对的辅助代理。

**本轮具体协助：** 核对任务书第6、14、15、16页的相关要求，核实本地路径、训练文件存在性及可复用运行环境，创建独立仓库、README 和忽略规则，执行初始 Git 提交，并提供第一小步的文件定位讲解。<span style="color: purple;">随后按用户授权运行文件定位命令；本次审阅目录中已有的未提交读取草稿、补充 mask 标签输出、运行固定训练样本并讲解代码，执行本步骤的真实提交。</span>

**审计与验证：** Codex 的自动检查已在上文明确列出；<span style="color: purple;"><s>用户尚未亲自运行本轮命令或回答理解问题。</s></span> <span style="color: purple;"><s>用户已正确回答文件名配对的理解问题；命令运行输出尚未提供，运行状态未经确认。</s></span> <span style="color: purple;">用户已正确回答文件名配对问题；文件定位及数组读取的运行输出均由 Codex 取得，数组读取理解核查待用户回答。</span>后续只在收到实际输出或回答后追加对应记录，不把自动检查写成用户验证，不把运行成功视为理解或原创性通过。

## <span style="color: purple;">逐步记录</span>

- <span style="color: purple;"><s>2026-10-25，文件名配对理解核查。用户亲自回答：“不能配对，因为 week_0 和 week_1 是不同时间点，即使病例编号和切片编号相同，也不能当作同一对。”</s></span> <span style="color: purple;">2026-10-25，文件名配对理解核查。此前的引语是扩写，现按本聊天实际答复修正为：“不能，因为 week_1 和 week_0 是不同时间点。”用户随后要求继续下一小步，并由 Codex 运行、逐步讲解代码。</span>
- <span style="color: purple;">Codex 核对结论：回答正确，体现了时间点必须一致这一配对条件；该回答不证明用户已运行文件定位命令，也不证明图像内容或空间对齐正确。Codex 根据本轮原始回答更新本说明。</span>
- <span style="color: purple;">Git：起步提交为 bcf428abd02316347d08776c0ae65a84c4aaea61；本条记录随本次实际文档提交保存，hash、时间及操作者以 git log 为准。</span>

### <span style="color: purple;">读取固定一对训练文件（2026-10-25）</span>

- <span style="color: purple;">问题与改动：把已定位的 NIfTI 文件读成可检查大小和数值的数组，为后续数据模块提供第一份运行证据。开始本步骤时已有未跟踪的 inspect_training_pair.py 短草稿；Codex 审阅并沿用该草稿，只补充 NumPy 导入及 mask 标签值输出，没有复制旧项目实现。</span>
- <span style="color: purple;">Codex 实际运行：在本仓库根目录，使用上文已核实的外部解释器执行 recognition/hipmri_2d_improved_unet/inspect_training_pair.py，退出码为 0。</span>
- <span style="color: purple;">实际输出：MRI shape: (256, 128)；Mask shape: (256, 128)；Mask labels: [0. 1. 2. 3.]。</span>
- <span style="color: purple;">核查结论：两数组均为二维且形状相同；此片 mask 中出现 0、1、2、3。get_fdata() 返回浮点数组，因此标签输出带小数点；未归一化、重标号、强制转整数或写回源文件。这不代表整个数据集只有四类，也不证明空间对齐正确。</span>
- <span style="color: purple;">用户理解状态：文件名配对已回答正确；本步仍待回答“mask 数值 2 表示亮度还是类别编号，以及依据是什么”。命令执行者为 Codex，不能记为用户亲自操作。</span>
- <span style="color: purple;">停止位置：只读取这一对训练文件，未创建 Dataset 类、预处理、可视化、模型或训练。与报告的对应关系是数据读取证据、真实渐进提交和 AI 使用披露。</span>
- <span style="color: purple;">Git：开始本步时最新提交为 527f892fc796a204ae3c2c4d2483e7aed4e0e259；本步骤的实际 hash、时间、作者和改动列表以 git log 为准。</span>
