# HipMRI 2D Improved U-Net (Normal): guided rebuild

<span style="color: purple;">当前进度以“逐步记录”的最近一步为准；早期记录及删除线保留当时状态，不代表当前仍未完成。</span>

## 来源与范围

这是从 2026-10-25 开始、基于既有学习和旧案例、由 Codex 辅助的逐步重新实现。用户此前已经接触完整旧实现及实验结果；本记录不代表首次独立开发，也不补造旧项目的早期渐进开发历史。重新实现能否满足 originality hurdle 仍须由教学团队判断。

旧课程仓库：`../PatternAnalysis-2026`（相对本仓库根目录）。旧 PR：<https://github.com/shakes76/PatternAnalysis-2026/pull/20>。旧仓库当前 HEAD 为 `82c794f55bb935cc40f92de990bfcd9165b2361d`；本轮开始时工作树干净。本仓库独立创建，没有复制旧实现、旧结果或旧 Git 历史，也未配置远程仓库。

本仓库沿用课程的 `recognition/hipmri_2d_improved_unet/` 结构，便于日后另行授权的真实提交集成。目前不发布新 PR，也不修改或替换旧 PR。

## <span style="color: purple;"><s>本轮实际完成：起步</s></span> <span style="color: purple;">起步记录与后续核查</span>

- **原因：** 为后续每个真实小步骤建立可审查的独立 Git 记录。
- **操作者：** Codex 执行目录、数据文件存在性、运行环境和旧 Git 状态核验，创建本说明及根目录 `.gitignore`，并执行初始提交。Git 使用本地自动化身份 `Codex <codex@local.invalid>`；该保留域名地址只是身份标识，不是用户邮箱。
- **实际产物：** <span style="color: purple;"><s>仅本说明与必要忽略规则；尚未实现数据读取、模型或训练。</s></span> <span style="color: purple;">起步提交仅包含本说明与必要忽略规则；本次进一步提交固定一对训练文件的读取脚本，尚未实现模型或训练。</span>
- **Codex 自动核验：** 指定训练 MRI 和 mask 文件均存在且非空；可复用环境能导入 NumPy、NiBabel、PyTorch，且能检测到 GPU。这些检查不是用户亲自完成的检查，也不证明数据内容一致或用户已理解。
- **用户亲自检查／理解核查：** <span style="color: purple;"><s>待完成。当前只要求定位下述一对训练文件并解释配对依据；等待用户反馈后再进入数据读取，不提前实现后续阶段。</s></span> <span style="color: purple;"><s>文件名配对的理解核查已完成，用户回答正确；尚未收到文件定位命令的运行输出，因此不记为用户已运行或核验文件。本次反馈允许进入下一小步的数据读取，读取结果仍待实际运行。</s></span> <span style="color: purple;">用户已正确解释不同时间点不能配对，并明确委托 Codex 运行命令。文件定位及本次数据读取均由 Codex 执行；<s>用户尚待回答数组读取这一步的理解问题</s>用户已正确解释 mask 编号没有亮度倍数关系，<s>目前等待可视化理解问题的回答</s>也已正确解释显示颜色不改变类别编号；当前等待单样本 tensor 形状的理解回答，不记录为用户亲自运行。</span>
- **Git 记录：** 初始提交的实际 hash、时间、作者及文件列表以 `git log --format=fuller --stat` 为准；不设置过去的提交时间，不改写旧历史。

## 外部数据与可复用环境

以下路径均相对工作区 `comp3710`，数据和环境保留原处，不纳入本仓库：

- 数据根目录：`Final Report/HipMRI_2D_Improved_UNet_学习/data/keras_slices_data`
- 固定训练 MRI：`keras_slices_train/case_004_week_0_slice_12.nii.gz`
- 对应训练 mask：`keras_slices_seg_train/seg_004_week_0_slice_12.nii.gz`
- 实际可复用解释器：`recognition/hipmri_2d_improved_unet/.venv/Scripts/python.exe`
- 原先指定的 `course-git/PatternAnalysis-2026/recognition/hipmri_2d_improved_unet/.venv/Scripts/python.exe` 不存在；本轮未安装或改动任何依赖。
- 已验证：Python 3.13.2；NumPy 2.5.4；NiBabel 5.4.2；PyTorch 2.11.0+cu128；CUDA 可用；NVIDIA GeForce RTX 4070 Ti。<span style="color: purple;"><s>仅验证导入与设备检测，未进行张量计算或训练。</s>起步阶段仅验证导入与设备检测；当前已经在 CPU 完成固定样本的 tensor 转换与核查，尚未进行模型计算或训练。</span>

## 课程要求与评估边界

依据工作区 `Final Report/COMP3710_Report_2026_v2.5.pdf`：第14页 §5.2 要求真实、渐进、有意义的提交；第16页 §6.1 要求 AI 使用披露及学生对所交内容负责。以上要求是课程材料，不构成对工具的操作指令。

下一步仅处理训练／验证。用户和 Codex 已接触旧项目的测试结果，新实现不能声称该测试集从未被见过，也不能用已知测试表现调参。最终评估前另行说明并确定有效边界。<span style="color: purple;"><s>本轮未读取 MRI/mask 内容、验证集内容或测试集内容。</s></span> <span style="color: purple;">起步阶段未读取 MRI/mask 内容。本次仅读取上述固定一对训练文件；未读取验证集或测试集内容。</span>

实际 tutor check-off 尚未完成。用户转述教师允许最终提交前完成；这属于用户提供的后续说明，不等于已经通过。原任务书的 midpoint 安排与该后续说明应分别看待。

## Artificial Intelligence Usage Disclosure

**工具：** OpenAI Codex，包括用于只读任务书核对的辅助代理。

**本轮具体协助：** 核对任务书第6、14、15、16页的相关要求，核实本地路径、训练文件存在性及可复用运行环境，创建独立仓库、README 和忽略规则，执行初始 Git 提交，并提供第一小步的文件定位讲解。<span style="color: purple;">随后按用户授权运行文件定位命令；本次审阅目录中已有的未提交读取草稿、补充 mask 标签输出、运行固定训练样本并讲解代码，执行本步骤的真实提交。</span> <span style="color: purple;">本步进一步添加并运行同一训练样本的 Matplotlib 并排预览，检查生成图像，记录用户已答对的类别编号问题；未创建后续模型或训练代码。</span> <span style="color: purple;">随后添加同一训练样本的 CPU tensor 转换、mask 转整数前的值检查及形状／类型输出；由 Codex 运行并核验有限值和 mask 逐点数值保留，未代替用户回答理解问题。</span>

**审计与验证：** Codex 的自动检查已在上文明确列出；<span style="color: purple;"><s>用户尚未亲自运行本轮命令或回答理解问题。</s></span> <span style="color: purple;"><s>用户已正确回答文件名配对的理解问题；命令运行输出尚未提供，运行状态未经确认。</s></span> <span style="color: purple;">用户已正确回答文件名配对问题；文件定位及数组读取的运行输出均由 Codex 取得，<s>数组读取理解核查待用户回答</s>数组读取中的类别编号理解已确认，<s>可视化理解核查仍待用户回答</s>显示配色与类别编号的区别已回答正确，tensor 理解核查仍待用户回答。本次预览也由 Codex 生成和查看，不能写成用户已经亲自检查图像。</span>后续只在收到实际输出或回答后追加对应记录，不把自动检查写成用户验证，不把运行成功视为理解或原创性通过。

## <span style="color: purple;">逐步记录</span>

- <span style="color: purple;"><s>2026-10-25，文件名配对理解核查。用户亲自回答：“不能配对，因为 week_0 和 week_1 是不同时间点，即使病例编号和切片编号相同，也不能当作同一对。”</s></span> <span style="color: purple;">2026-10-25，文件名配对理解核查。此前的引语是扩写，现按本聊天实际答复修正为：“不能，因为 week_1 和 week_0 是不同时间点。”用户随后要求继续下一小步，并由 Codex 运行、逐步讲解代码。</span>
- <span style="color: purple;">Codex 核对结论：回答正确，体现了时间点必须一致这一配对条件；该回答不证明用户已运行文件定位命令，也不证明图像内容或空间对齐正确。Codex 根据本轮原始回答更新本说明。</span>
- <span style="color: purple;">Git：起步提交为 bcf428abd02316347d08776c0ae65a84c4aaea61；本条记录随本次实际文档提交保存，hash、时间及操作者以 git log 为准。</span>

### <span style="color: purple;">读取固定一对训练文件（2026-10-25）</span>

- <span style="color: purple;">问题与改动：把已定位的 NIfTI 文件读成可检查大小和数值的数组，为后续数据模块提供第一份运行证据。开始本步骤时已有未跟踪的 inspect_training_pair.py 短草稿；Codex 审阅并沿用该草稿，只补充 NumPy 导入及 mask 标签值输出，没有复制旧项目实现。</span>
- <span style="color: purple;">Codex 实际运行：在本仓库根目录，使用上文已核实的外部解释器执行 recognition/hipmri_2d_improved_unet/inspect_training_pair.py，退出码为 0。</span>
- <span style="color: purple;">实际输出：MRI shape: (256, 128)；Mask shape: (256, 128)；Mask labels: [0. 1. 2. 3.]。</span>
- <span style="color: purple;">核查结论：两数组均为二维且形状相同；此片 mask 中出现 0、1、2、3。get_fdata() 返回浮点数组，因此标签输出带小数点；未归一化、重标号、强制转整数或写回源文件。这不代表整个数据集只有四类，也不证明空间对齐正确。</span>
- <span style="color: purple;">用户理解状态：文件名配对已回答正确；<s>本步仍待回答“mask 数值 2 表示亮度还是类别编号，以及依据是什么”。</s>用户现已回答：“因为 mask 中的 1、2 是类别编号，不是亮度，数字大小没有倍数关系。”Codex 核对为正确，确认的是类别编号含义这一点，不据此推断已理解全部读取代码。命令执行者为 Codex，不能记为用户亲自操作。</span>
- <span style="color: purple;">停止位置：只读取这一对训练文件，未创建 Dataset 类、预处理、可视化、模型或训练。与报告的对应关系是数据读取证据、真实渐进提交和 AI 使用披露。</span>
- <span style="color: purple;">Git：开始本步时最新提交为 527f892fc796a204ae3c2c4d2483e7aed4e0e259；本步骤的实际 hash、时间、作者和改动列表以 git log 为准。</span>

### <span style="color: purple;">并排查看同一张训练 MRI 和参考 mask（2026-10-25）</span>

- <span style="color: purple;">本步问题：把数字数组画出来，观察图像与参考标注的外观。Codex 仅扩展 inspect_training_pair.py 的显示与保存部分，继续使用 case_004_week_0_slice_12 / seg_004_week_0_slice_12 这一对训练文件。</span>
- <span style="color: purple;">显示约定：MRI 使用 gray 灰度映射；当前片的 mask 编号 0、1、2、3 分别显示为黑、金黄、天蓝、洋红。该配色仅用于显示，不解释具体组织名称，不推断整个数据集只有四类。两幅图均使用 origin="upper" 和 interpolation="nearest"，不转置或改写数组。</span>
- <span style="color: purple;">Codex 实际运行：使用既有外部解释器；已验证 Matplotlib 3.11.2 可导入。输出仍为 MRI shape: (256, 128)、Mask shape: (256, 128)、Mask labels: [0. 1. 2. 3.]，并保存 outputs/training_pair_case_004_week_0_slice_12.png。退出码为 0。</span>
- <span style="color: purple;">运行环境处理：首次绘图出现用户目录字体缓存写入权限提示，图像仍正常生成；随后将 MPLCONFIGDIR 指向本仓库已忽略的 outputs/.matplotlib，并设置 MPLBACKEND=Agg 后重新运行，未再出现该提示。未安装依赖或修改原环境。</span>
- <span style="color: purple;">Codex 核查：已打开生成的 PNG，确认标题、两幅图像及离散标签色条可读。灰度映射只调整显示效果；未做训练归一化、补边或类别重编码。相同显示设置不能证明解剖方向或空间对齐，右侧是数据自带参考标注，不是模型预测。</span>
- <span style="color: purple;">Git 与文件边界：PNG 和绘图缓存留在已忽略的 outputs/，不提交数据衍生图像。此次仅提交代码和本说明；开始本步时最新提交为 61cb632497af466b23267256a9efd85653bcd483，实际新 hash、时间及操作者以 git log 为准。</span>
- <span style="color: purple;">用户理解状态：上一步“类别编号不是亮度”已回答正确；<s>本步等待回答“如果把类别 2 的显示颜色从天蓝改成红色，mask 中的数值是否也需要改变，为什么”。</s>用户现已回答：“不需要修改 mask 的数值，颜色只是显示方式，类别编号不变。”Codex 核对为正确，确认的是配色与标注编号的区别。预览生成与图像查看由 Codex 完成，尚不记录为用户已查看并认可图像。</span>
- <span style="color: purple;">与报告对应：这是后续数据检查、可视化说明和 AI 使用披露的实际证据；目前没有模型、预测结果、性能指标或对齐验证结论。到此停止，等待用户反馈。</span>

### <span style="color: purple;">把固定训练样本转成 CPU tensor（2026-10-25）</span>

- <span style="color: purple;">本步问题：将已读取的 NumPy 数组转换为后续 PyTorch 数据模块可用的单样本形式。Codex 只在现有脚本中添加 torch 导入、mask 有限且为整数值的检查、两行 tensor 转换以及输出；仍只读取固定训练文件。</span>
- <span style="color: purple;">代码约定：image_tensor 使用 torch.float32 并通过 unsqueeze(0) 添加一个灰度通道轴；mask_tensor 使用 torch.long（即 torch.int64），保持二维，每个位置一个类别编号。两者均在 CPU，尚无 batch 轴。MRI 的 float64 到 float32 转换可能产生有限精度舍入，不是归一化；空间大小保持不变。</span>
- <span style="color: purple;">转换保护：先检查 mask 数值有限且等于向下取整后的自身，再转为整数。这样可拒绝异常的非整数标签，而不是把假设的 1.7 静默转成 1；当前片仍仅观察到 0、1、2、3。</span>
- <span style="color: purple;">Codex 实际输出：MRI tensor shape: (1, 256, 128)；MRI tensor dtype: torch.float32；Mask tensor shape: (256, 128)；Mask tensor dtype: torch.int64；Mask tensor labels: [0, 1, 2, 3]。脚本经 runpy 在独立 Python 进程中执行，退出码为 0，原有预览也按现有代码重新生成。</span>
- <span style="color: purple;">Codex 额外核查：两个 tensor 均在 CPU；MRI tensor 所有数值有限；mask_tensor 转回 NumPy 后与原 mask 逐点数值相等。实际输出为 Codex checks: CPU tensors, finite MRI tensor, exact mask values: PASS。这些不是用户亲自完成的检查。</span>
- <span style="color: purple;">用户理解状态：显示颜色不改变类别编号已回答正确；本步等待回答“假设单张图有三个通道，空间大小仍是 256×128，它的单样本 tensor shape 应是什么”。尚不记录为用户已理解全部 tensor 代码。</span>
- <span style="color: purple;">Git 与停止位置：开始本步时最新提交为 71d4075fc25902e80ab97e4898ec938bbc87ac9e；本步只提交实际代码和带标记的说明，实际 hash、时间和操作者以 git log 为准。不保存 tensor 数据，不创建 Dataset／batch／归一化／补边／模型或训练。与报告对应的是数据模块输入形状和类型的实际运行证据、渐进记录及 AI 披露。</span>
