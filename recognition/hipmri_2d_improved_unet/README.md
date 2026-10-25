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
- **用户亲自检查／理解核查：** <span style="color: purple;"><s>待完成。当前只要求定位下述一对训练文件并解释配对依据；等待用户反馈后再进入数据读取，不提前实现后续阶段。</s></span> <span style="color: purple;"><s>文件名配对的理解核查已完成，用户回答正确；尚未收到文件定位命令的运行输出，因此不记为用户已运行或核验文件。本次反馈允许进入下一小步的数据读取，读取结果仍待实际运行。</s></span> <span style="color: purple;">用户已正确解释不同时间点不能配对，并明确委托 Codex 运行命令。文件定位及本次数据读取均由 Codex 执行；<s>用户尚待回答数组读取这一步的理解问题</s>用户已正确解释 mask 编号没有亮度倍数关系，<s>目前等待可视化理解问题的回答</s>也已正确解释显示颜色不改变类别编号；<s>当前等待单样本 tensor 形状的理解回答</s>单样本 tensor 通道轴已回答正确，<s>目前等待 min-max 归一化数值例的回答</s>归一化数值例也已回答正确，<s>目前等待 batch 形状理解问题的回答</s>batch 与通道数的区别已回答正确，<s>目前等待模块导入与函数复用的理解回答</s>函数复用理由已回答正确，<s>目前等待单样本读取函数返回顺序的理解回答</s>返回顺序已回答正确，<s>目前等待 Dataset 按编号取样的理解回答</s>Dataset 按编号取样已回答正确，<s>目前等待 DataLoader 分批数量的理解回答</s>DataLoader 分批已回答正确，<s>目前等待文件名逐对核查的理解回答</s>文件名逐对核查已回答正确，<s>目前等待患者分组独立性的理解回答</s>case 分组独立性已回答正确，<s>目前等待 sampler 索引与病例编号区别的理解回答</s>用户要求改按完整功能里程碑推进；该索引题未作答，不记为已理解，也不再作为推进门槛，不记录为用户亲自运行。</span>
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

<span style="color: purple;">2026-10-26资源记录与正式训练授权：用户正确解释参考图macro不能证明ID5效果，以及验证不能反向更新，并明确认可20轮方案及派生ID保留工作假设。Codex记录此确认，新增分阶段资源记录、推理性能入口、协议漂移与setup失败检查，再按批准方案执行训练／验证。自动检查、GPU运行与Git操作仍由Codex及辅助代理完成，不能记为用户亲自运行或独立实现。</span>

<span style="color: purple;">正式实验前修复与核查：Codex按用户后续审查要求添加像素读取前的shape／Affine检查、针对性检查及训练／验证全量头信息补充审计；核实CSIRO原始标签说明，并明确课程2D派生保留ID尚未独立确认。只读比较新旧源码，重新检查固定训练图及现有smoke权重的输入／恢复链路，准备正式实验方案。未新增真实MRI训练，未读取测试目录、文件名或像素；本轮用户整体核查和正式训练确认均保持待完成。</span>

**工具：** OpenAI Codex，包括用于只读任务书核对的辅助代理。

**本轮具体协助：** 核对任务书第6、14、15、16页的相关要求，核实本地路径、训练文件存在性及可复用运行环境，创建独立仓库、README 和忽略规则，执行初始 Git 提交，并提供第一小步的文件定位讲解。<span style="color: purple;">随后按用户授权运行文件定位命令；本次审阅目录中已有的未提交读取草稿、补充 mask 标签输出、运行固定训练样本并讲解代码，执行本步骤的真实提交。</span> <span style="color: purple;">本步进一步添加并运行同一训练样本的 Matplotlib 并排预览，检查生成图像，记录用户已答对的类别编号问题；未创建后续模型或训练代码。</span> <span style="color: purple;">随后添加同一训练样本的 CPU tensor 转换、mask 转整数前的值检查及形状／类型输出；由 Codex 运行并核验有限值和 mask 逐点数值保留，未代替用户回答理解问题。</span> <span style="color: purple;">本步添加逐片 min-max 归一化小函数，仅用于 MRI tensor；Codex 运行固定训练样本，并额外用构造的常量与 NaN 输入核查边界，记录为代码检查而非 MRI 实验结果。</span> <span style="color: purple;">随后仅添加单样本的 batch 轴及形状输出，由 Codex 核查取出样本后的数值／类型／设备保持，未实现 DataLoader 或训练。</span> <span style="color: purple;">本步将已实现的归一化函数原样移动到新 dataset.py，检查脚本改为导入；Codex 核验本地模块路径、导入行为以及整理前后实际输出和 tensor 一致。</span>

<span style="color: purple;">本步具体协助：Codex 添加 load_pair 单样本读取函数，将既有读取、类型转换与归一化流程集中到 dataset.py，改写检查脚本调用并核查与上一步准备后 tensor 的一致性。</span>

<span style="color: purple;">本步具体协助：Codex 添加只接收已核对路径清单的最小 HipMRIPairDataset，接入 len 与 [0]，运行固定样本并核验惰性读取、索引边界及准备后 tensor 与前一步的一致性；未生成目录扫描、DataLoader 或模型。</span>

<span style="color: purple;">本步具体协助：Codex 将当前单样本 Dataset 接入 DataLoader，替换手工 batch，运行并比较 tensor 一致性，单独跟踪取样时机、文件读取次数及同一迭代器的结束行为；未读取新案例或实现模型。</span>

<span style="color: purple;">本步具体协助：Codex 添加仅检查文件名与存在性的 collect_pairs 及独立训练清单检查脚本，扫描训练目录并核查固定参考对；临时空文件只用于缺配对与多余 mask 的代码检查，未读取更多 MRI 内容或接入全量 DataLoader。</span>

<span style="color: purple;">本步具体协助：Codex 按严格文件名格式提取数字 case 分组，统计训练与验证编号集合并检查交集；读取被阻断时审计仍通过，未修改划分、读取像素或扫描测试文件名。case 编号只作为当前患者分组代理。</span>

<span style="color: purple;">本步具体协助：Codex 将完整训练路径清单传给 Dataset，并为固定参考样本构造只含一条索引的参考 DataLoader；核对惰性构造、实际读取范围及与前一步的 tensor 一致性，没有遍历全量图像或训练。</span>

<span style="color: purple;">本里程碑新增协助：Codex 完成归一化、按16倍数向下／向右补边、有效区域与原尺寸记录、混合尺寸batch整理、原尺寸裁回及有效像素选择；编写构造检查和仅训练／验证的全量预处理审计。所有自动检查均由 Codex 执行，不作为用户亲自运行或理解的证明。</span>

<span style="color: purple;">Baseline里程碑新增协助：Codex 实现标准U-Net拓扑、有效区域one-hot CE、按split累计的指标、训练／验证与checkpoint保存恢复、仅训练／验证样本推理、曲线及构造检查；实际运行64个训练样本的2轮smoke并每轮验证全部660例。此为自动实现与验证，不记录为用户亲自完成或已理解全部模型。</span>

<span style="color: purple;">Improved里程碑新增协助：Codex 核对任务书Ref[2]及原论文，编写其2D改编模型、模型选择入口和检查；保留baseline及共用数据／loss／指标实现。复核时在真实训练前修正localization通道减半的位置；运行原baseline回归和Improved的固定64样本2轮smoke，每轮验证全部<s>660例</s>660个验证切片样本，核查权重恢复并查看训练参考预测图。代码、运行、文档与提交由Codex及辅助代理完成，不记录为用户独立实现、亲自运行或已理解整组代码。</span>

**审计与验证：** Codex 的自动检查已在上文明确列出；<span style="color: purple;"><s>用户尚未亲自运行本轮命令或回答理解问题。</s></span> <span style="color: purple;"><s>用户已正确回答文件名配对的理解问题；命令运行输出尚未提供，运行状态未经确认。</s></span> <span style="color: purple;">用户已正确回答文件名配对问题；文件定位及数组读取的运行输出均由 Codex 取得，<s>数组读取理解核查待用户回答</s>数组读取中的类别编号理解已确认，<s>可视化理解核查仍待用户回答</s>显示配色与类别编号的区别已回答正确，<s>tensor 理解核查仍待用户回答</s>单样本通道轴理解已回答正确，<s>归一化理解仍待用户回答</s>归一化数值例已回答正确，<s>batch 理解仍待用户回答</s>batch 形状理解已回答正确，<s>模块导入理解仍待用户回答</s>函数复用理由已回答正确，<s>load_pair 返回顺序的理解仍待用户回答</s>返回顺序已回答正确，<s>Dataset 按编号取样的理解仍待用户回答</s>Dataset 按编号取样已回答正确，<s>DataLoader 分批理解仍待用户回答</s>DataLoader 分批已回答正确，<s>文件名配对核查的理解仍待用户回答</s>文件名配对核查已回答正确，<s>患者分组独立性的理解仍待用户回答</s>case 分组独立性已回答正确，<s>sampler 索引选择的理解仍待用户回答</s>该题未作答；现按用户指定的功能里程碑完成代码、自动检查及整体讲解。本次预览也由 Codex 生成和查看，不能写成用户已经亲自检查图像。</span>后续只在收到实际输出或回答后追加对应记录，不把自动检查写成用户验证，不把运行成功视为理解或原创性通过。

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
- <span style="color: purple;">用户理解状态：显示颜色不改变类别编号已回答正确；<s>本步等待回答“假设单张图有三个通道，空间大小仍是 256×128，它的单样本 tensor shape 应是什么”。</s>用户现已回答：“应该是 (3, 256, 128)，最前面的 3 表示通道数。”Codex 核对为正确，确认的是单样本通道轴这一点。尚不记录为用户已理解全部 tensor 代码。</span>
- <span style="color: purple;">Git 与停止位置：开始本步时最新提交为 71d4075fc25902e80ab97e4898ec938bbc87ac9e；本步只提交实际代码和带标记的说明，实际 hash、时间和操作者以 git log 为准。不保存 tensor 数据，不创建 Dataset／batch／归一化／补边／模型或训练。与报告对应的是数据模块输入形状和类型的实际运行证据、渐进记录及 AI 披露。</span>

### <span style="color: purple;">对固定训练 MRI 做逐片 min-max 归一化（2026-10-25）</span>

- <span style="color: purple;">本步问题与选择：将这张训练 MRI 的强度缩放到 0～1，便于核查后续输入范围。这是本实现当前选择的逐片预处理方案，不是课程指定方案，也未证明优于其他 MRI 归一化方法。min/max 只从当前这一张训练 MRI 取得，未汇总验证集或测试集统计。</span>
- <span style="color: purple;">实际改动：Codex 在现有脚本添加 minmax_normalize(values) 小函数：拒绝非有限数值；非恒定图按 (values-min)/(max-min) 转换；若 max=min 则返回同形状全零 tensor，避免除零。结果保存在新变量 normalized_image，原 image_tensor 和 mask_tensor 不参与原地修改。</span>
- <span style="color: purple;">真实样本输出：MRI range before: 0.0 438.0；MRI range after: 0.0 1.0；Normalized MRI shape: (1, 256, 128)；Normalized MRI dtype: torch.float32；Mask labels after MRI normalization: [0, 1, 2, 3]。仍只处理 case_004_week_0_slice_12 与对应训练 mask。</span>
- <span style="color: purple;">Codex 真实样本核查：归一化结果全部有限，最小值 0、最大值 1，shape／dtype／CPU device 保留；原始 image_tensor 仍等于原 MRI 数组转换后的 float32 tensor；mask 与原标注逐点数值相同。检查实际通过，脚本退出码为 0。原有预览代码继续显示原数组，没有新增归一化对照图。</span>
- <span style="color: purple;">Codex 构造的边界核查：全为 5 的 1×2×2 float32 tensor 返回全零，输入保持不变；含 NaN 的小 tensor 抛出 ValueError。两项均通过。这是构造数据上的代码核查，不是额外 MRI 实验、用户亲自操作或模型性能证据。</span>
- <span style="color: purple;">用户理解状态：三通道单样本 shape 已回答正确；<s>本步等待回答“本片最小值 0、最大值 438，假设某个像素强度为 219，归一化后是多少”。</s>用户现已回答：“归一化后是 0.5，因为 (219 - 0) / (438 - 0) = 0.5。”Codex 核对为正确，确认本数值例的理解。219 是理解题假设值，不声称检查过某个真实像素为 219。</span>
- <span style="color: purple;">Git 与停止位置：开始本步时最新提交为 41b3497f561c18e6ae09f8a5ad64f57769850d5d；此次仅提交实际脚本与带标记的说明，实际新 hash／时间／作者以 git log 为准。到此停止，不创建补边、batch、Dataset、模型或训练。与报告对应的是预处理选择及实际数值核查、渐进开发证据和 AI 披露。</span>

### <span style="color: purple;">手工组成 batch size 1（2026-10-25）</span>

- <span style="color: purple;">本步问题：为后续按批处理准备外层样本轴。Codex 仅对同一张训练 MRI 的 normalized_image 和对应 mask_tensor 各调用一次 unsqueeze(0)，插入长度为 1 的 batch 轴，并添加三行形状／样本数输出。</span>
- <span style="color: purple;">形状约定：图像为 [B,C,H,W]，类别编号 mask 为 [B,H,W]。当前 B=1、C=1、H=256、W=128；图像形状中的前两个 1 分别表示样本数和通道数，mask 没有增加通道轴。这是手工组成的单样本 batch，不是 DataLoader 或多样本读取。</span>
- <span style="color: purple;">Codex 实际输出：MRI batch shape: (1, 1, 256, 128)；Mask batch shape: (1, 256, 128)；Batch size: 1。只读取原固定训练样本，既有预览照常生成，脚本经 runpy 执行，退出码为 0。</span>
- <span style="color: purple;">Codex 核查：图像与 mask 的 batch size 均为 1；取 image_batch[0] 与 mask_batch[0] 后，分别与加轴前的 normalized_image 和 mask_tensor 逐点相等；dtype 和 device 保持。实际输出检查通过。插入轴没有增加第二张图像或新的训练案例。</span>
- <span style="color: purple;">用户理解状态：归一化数值例已回答正确；<s>本步等待回答“如果以后一个 batch 放两张同样大小的单通道 MRI，图像 batch shape 应是什么”。</s>用户现已回答：“应该是 (2, 1, 256, 128)，最前面的 2 表示 batch 中有两张图，后面的 1 表示每张图只有一个通道。”Codex 核对为正确，确认 batch 轴与通道轴的区别。两张图是理解题假设，本轮没有读取第二张 MRI。上述执行与核查均由 Codex 完成。</span>
- <span style="color: purple;">Git 与停止位置：开始本步时最新提交为 3fa20d99c8ad1db9e5b524f89fe033a51d0b856a；此次仅提交实际代码与带标记的说明，实际新 hash／时间／作者以 git log 为准。到此停止，不创建 DataLoader、Dataset、补边、模型或训练。与报告对应的是后续训练输入及目标形状的运行证据、渐进开发记录和 AI 披露。</span>

### <span style="color: purple;">将归一化函数移到 dataset.py（2026-10-25）</span>

- <span style="color: purple;">本步问题：让已验证的数据处理小工具能被其他脚本复用。Codex 新建 dataset.py，仅包含模块说明、torch 导入和原样的 minmax_normalize 函数；inspect_training_pair.py 删除本地重复定义，改用 from dataset import minmax_normalize，调用方式保持不变。</span>
- <span style="color: purple;">实际代码边界：dataset.py 的顶层不包含 MRI 路径、数据读取、绘图或打印，也没有 Dataset 类。导入该模块提供函数；读取固定样本和保存预览仍由检查脚本执行。本步是代码整理与模块复用，没有新增归一化算法。</span>
- <span style="color: purple;">Codex 导入核查：明确确认 dataset.__file__ 指向本项目新文件；导入没有打印输出或重写预览。检查程序使用 runpy 时显式加入本项目目录，以保持与直接运行检查脚本时相同的本地模块查找范围。</span>
- <span style="color: purple;">Codex 行为保持核查：从本重建仓库的上一次提交读取原脚本，与整理后的脚本分别处理同一个固定训练样本；两次标准输出完全一致。函数语法结构保持相同，image_tensor、mask_tensor、normalized_image、image_batch、mask_batch 五个 tensor 逐点值／dtype／device 全部一致。退出码为 0，未调用旧课程项目实现或读取其他训练案例。</span>
- <span style="color: purple;">实际输出仍为 MRI range before: 0.0 438.0；MRI range after: 0.0 1.0；MRI batch shape: (1, 1, 256, 128)；Mask batch shape: (1, 256, 128)；Batch size: 1；mask 标签 [0, 1, 2, 3]。上述核查由 Codex 执行，不是用户亲自运行。</span>
- <span style="color: purple;">用户理解状态：batch 与通道轴的区别已回答正确；<s>本步等待回答“假设另一个脚本也需要相同归一化，应复制一份函数还是导入 dataset.py 中已有函数，为什么”。尚不记录为用户已经理解模块导入。</s>用户现已回答：“应该导入 dataset.py 中已有的函数，避免重复代码，以后修改归一化逻辑时只需改一处。”Codex 核对为正确，确认函数复用与集中维护的理由；尚不据此推断用户已独立完成模块实现。</span>
- <span style="color: purple;">Git 与停止位置：开始本步时最新提交为 54a03cf0b6facd93d3370c2a51dd520a05914adb；仅提交新数据辅助模块、检查脚本的实际整理及带标记的说明，实际新 hash／时间／作者以 git log 为准。与报告对应的是 dataset.py 数据模块的起步及代码组织说明；未实现 Dataset 类、DataLoader、补边、模型或训练。到此停止，等待用户反馈。</span>

### <span style="color: purple;">建立 load_pair 单样本读取函数（2026-10-25）</span>

- <span style="color: purple;">本步问题：用一次函数调用取得后续可用的一对单样本 tensor。Codex 在 dataset.py 添加 load_pair(image_path, mask_path)，读取两个 NIfTI 数组，检查二维及同 shape、mask 数值有限且为整数，然后转换图像为 float32 [1,H,W]、mask 为 int64 [H,W]，调用已有归一化函数，按顺序返回归一化图像和 mask。</span>
- <span style="color: purple;">输入边界：函数接受调用方已核对文件名的一对路径，不扫描目录，不自动验证病例／时间点／切片编号，也不证明空间对齐。当前仍仅使用已核对的 case_004_week_0_slice_12 与对应 seg 训练文件，没有读取新的病例或验证／测试数据。</span>
- <span style="color: purple;">检查脚本实际改动：使用 normalized_image, mask_tensor = load_pair(image_path, mask_path)，移除脚本中重复的 mask 检查、类型转换和归一化实现，并整理重复输出。为保留原始 MRI 范围及预览，脚本仍读取原始数组；新函数还会读取同一对文件，因此当前检查流程存在同一样本的重复读取，不把它称作最终高效流水线或多个独立案例。</span>
- <span style="color: purple;">Codex 实际输出：MRI range before: 0.0 438.0；MRI range after: 0.0 1.0；Normalized MRI shape: (1, 256, 128)；Normalized MRI dtype: torch.float32；Mask tensor shape: (256, 128)；Mask tensor dtype: torch.int64；标签 [0, 1, 2, 3]。检查脚本随后仍手工组成 batch size 1，图像为 (1, 1, 256, 128)、mask 为 (1, 256, 128)。</span>
- <span style="color: purple;">Codex 核查：确认调用的是本地 dataset.py；从本重建仓库上次提交取得检查脚本作为比较对象。normalized_image、mask_tensor、image_batch、mask_batch 四个 tensor 的值／dtype／device 与上一步一致，mask 逐点保留原标注编号，读取函数返回时尚无 batch 轴。脚本与核查退出码为 0，没有调用旧课程项目实现。</span>
- <span style="color: purple;">用户理解状态：复用已有函数的理由已回答正确；<s>本步等待回答“若把接收语句写成 mask_tensor, normalized_image = load_pair(image_path, mask_path)，能否仍正确接收图像和 mask，为什么”。</s>用户现已回答：“不能，函数按顺序返回图像和 mask，交换左边变量名会把图像赋给 mask_tensor、把 mask 赋给 normalized_image。”Codex 核对为正确，确认按位置接收返回结果这一点。命令和一致性检查均由 Codex 执行，不记录为用户已亲自运行或理解整个读取流程。</span>
- <span style="color: purple;">Git 与停止位置：开始本步时最新提交为 36e9d2454620237b9aee42830e9c10a3ff3a240c；只提交实际数据辅助模块、检查脚本及带标记的说明，实际新 hash／时间／作者以 git log 为准。与报告对应的是 dataset.py 中单样本读取与预处理接口的运行证据；尚未实现 Dataset 类、DataLoader、补边、模型或训练。到此停止，等待用户反馈。</span>

### <span style="color: purple;">建立只含固定训练样本的最小 Dataset（2026-10-25）</span>

- <span style="color: purple;">本步问题：让一份样本路径清单能报告长度，并按编号提供单个样本。Codex 在 dataset.py 添加继承 PyTorch Dataset 的 HipMRIPairDataset；__init__ 只把调用方提供的已核对路径对存为列表，__len__ 返回列表长度，__getitem__ 取出指定路径对并调用现有 load_pair。</span>
- <span style="color: purple;">检查脚本实际改动：使用 HipMRIPairDataset([(image_path, mask_path)]) 创建只有一条记录的训练清单，打印 len(training_dataset)，再用 training_dataset[0] 获取归一化图像和 mask。列表中每条记录是一对路径，两份文件合为一个带标注样本。Dataset 返回时没有 batch 轴，既有手工 batch 代码保留。</span>
- <span style="color: purple;">Codex 实际输出：Dataset samples: 1；Normalized MRI shape: (1, 256, 128)，dtype torch.float32，范围 0.0～1.0；Mask tensor shape: (256, 128)，dtype torch.int64，标签 [0, 1, 2, 3]；既有 batch 图像 (1, 1, 256, 128)、mask (1, 256, 128)。仍只读取原固定训练文件。</span>
- <span style="color: purple;">Codex 接口核查：临时让 NIfTI 读取函数在被调用时立即失败，验证 Dataset 自身的构造与 len 不触发读取；单元素清单的索引 1 抛出 IndexError；空清单长度为 0、索引 0 抛出 IndexError。空清单属于接口边界检查，不是新的 MRI 实验；没有声称负索引都非法。检查脚本用于原始预览的独立读取仍存在，这与 Dataset 自身按需读取的行为分别记录。</span>
- <span style="color: purple;">Codex 真实样本核查：与本重建仓库上一次提交中的检查脚本比较，normalized_image、mask_tensor、image_batch、mask_batch 四个 tensor 的值／dtype／device 保持一致，检查退出码为 0。上述执行与自动核查由 Codex 完成。</span>
- <span style="color: purple;">用户理解状态：返回结果按位置接收已回答正确；<s>本步等待回答“假设路径清单有十对，执行 training_dataset[0] 会让 Dataset 读取全部十对还是第一对，为什么”。</s>用户答复要点（转述）：只读取第一对，按编号 0 取出路径交给 load_pair，不遍历整个清单。Codex 核对为正确，确认 Dataset 按编号取样这一点。十对是理解题假设，当前清单仍仅一对；<s>尚不记录为用户已理解 Dataset 类。</s>不据此推断用户已经理解全部 Dataset 类代码。</span>
- <span style="color: purple;">Git 与停止位置：开始本步时最新提交为 6a8b7ecc9134ae4bddac14c54ed6d96021b8d0e7；仅提交实际数据模块、检查脚本和带标记说明，实际新 hash／时间／作者以 git log 为准。与报告对应的是 dataset.py 中最小按编号取样接口及真实运行证据；尚无自动配对、目录扫描、患者划分、DataLoader、补边、模型或训练。到此停止，等待用户反馈。</span>

### <span style="color: purple;">用 DataLoader 取出当前单样本 batch（2026-10-25）</span>

- <span style="color: purple;">本步问题：让 PyTorch 自动调用 Dataset 并组成 batch。Codex 仅在检查脚本创建 DataLoader(training_dataset, batch_size=1, shuffle=False, num_workers=0)，保留默认 drop_last=False；用 next(iter(training_loader)) 取第一批，替换此前手工 unsqueeze 的 batch。当前设置用于固定样本接口核查，不是已经选定的正式训练配置。</span>
- <span style="color: purple;">取样与诊断：Dataset 仍仅一条已核对的训练路径对；batch 自动组成后，image_batch[0] 和 mask_batch[0] 供原有单样本输出使用，不再为这些诊断单独调用 Dataset[0]。原始 MRI 预览的独立读取仍保留。未读取第二个病例、验证集或测试集。</span>
- <span style="color: purple;">Codex 实际输出：Dataset samples: 1；DataLoader batches: 1；MRI batch shape: (1, 1, 256, 128)；Mask batch shape: (1, 256, 128)；Batch size: 1。归一化范围仍为 0.0～1.0，mask 标签 [0, 1, 2, 3]，图像 float32、mask int64。</span>
- <span style="color: purple;">Codex 数值核查：与本重建仓库上一提交的手工 batch 比较，normalized_image、mask_tensor、image_batch、mask_batch 四个 tensor 的逐点值／dtype／device 均一致，运行退出码为 0。这里只替换取样与组 batch 的方式，没有模型输出或训练性能结果。</span>
- <span style="color: purple;">Codex 迭代器核查：只在 DataLoader 操作范围内计数 NIfTI 读取。num_workers=0 时，构造 loader、查询长度及创建 iterator 均未读取文件；第一次 next(iterator) 恰好读取当前 MRI 和 mask 两个路径；再次 next 同一个 iterator 抛出 StopIteration，未增加读取。重新调用 iter(loader) 会开始一个新迭代器，不能将它与继续同一个迭代器混淆。该计数不包含脚本为原图预览进行的独立读取。</span>
- <span style="color: purple;">用户理解状态：Dataset 按编号只取目标样本已回答正确；<s>本步等待回答“假设 Dataset 有五个样本，batch_size=2，默认保留不足一批的末批，各批会有几张图”。</s>用户现已回答：“会分成三批，分别有 2、2、1 张图，因为默认保留最后不足一批的样本。”Codex 核对为正确，确认末批保留与分批计数这一点。五个样本仅为理解题假设，当前实际仍是一对训练文件；以上运行和核查由 Codex 执行。</span>
- <span style="color: purple;">Git 与停止位置：开始本步时最新提交为 2af3fcfe8fe2df5a0e1b30d9d35391fa4ac4aa8b；只提交实际检查脚本和带标记说明，实际新 hash／时间／作者以 git log 为准。与报告对应的是从 Dataset 到 batch 的数据输入链路及运行证据；尚无目录扫描、自动配对、患者划分、补边、模型或训练。到此停止，等待用户反馈。</span>

### <span style="color: purple;">只按文件名建立训练路径配对清单（2026-10-25）</span>

- <span style="color: purple;">本步问题：替代手写大量路径，按完整文件名建立 MRI/mask 对应关系。Codex 在 dataset.py 添加 collect_pairs(image_dir, mask_dir)：只找 case_*.nii.gz 文件，稳定排序；只把每个 MRI 文件名的第一个 case_ 前缀换为 seg_，在 mask 目录检查对应文件存在，再保存路径对。sorted 只稳定顺序，字符串排序不代表切片数值或解剖顺序；配对依据是病例／时间点／切片编号部分保持一致。</span>
- <span style="color: purple;">检查边界：空 MRI 文件清单报错；某个 MRI 没有对应 mask 时报告缺失路径；每个 MRI 均逐名匹配后，再核对 seg_*.nii.gz 文件数，拒绝多余 mask。两侧仅统计 is_file() 为真的路径，忽略同名目录。没有仅凭数量相同或 zip 两份排序清单来猜配对。</span>
- <span style="color: purple;">实际运行：新增独立 inspect_training_pairs.py，仅扫描 keras_slices_train 与 keras_slices_seg_train。输出 Paired training filenames: 11460；Reference pair found: True。固定 case_004_week_0_slice_12 与对应 seg 路径在清单中；未发现符合匹配样式的缺失／多余 mask。11460 是训练切片路径对数，不是患者数或已逐个读取验证的数据量。</span>
- <span style="color: purple;">Codex 真实目录核查：清单无重复路径对，每个 mask 名均按对应 MRI 名准确替换前缀；临时阻断 nib.load 时扫描仍成功，确认函数未读取 NIfTI 内容。本轮没有打开更多 MRI 像素、验证集或测试集内容，也未扫描后两者文件名。</span>
- <span style="color: purple;">Codex 构造的文件名核查：在已忽略 outputs/ 下的临时目录中创建空文件，验证正常两对可匹配、空 MRI 清单／缺 mask／多余 mask 会报错，同名目录不计为文件。检查通过后清理临时目录。这些空文件不是可用 MRI，不是医学实验或训练样本。</span>
- <span style="color: purple;">当前限制：只证明文件名对应和路径存在，不证明 NIfTI 可读取、全量 shape／标签正确、空间对齐或患者划分无泄漏。原单样本 Dataset/DataLoader 脚本保持不变，仍未把 11460 对清单接入训练或 DataLoader；患者划分需另一步实际核查。</span>
- <span style="color: purple;">用户理解状态：DataLoader 末批分组已回答正确；<s>本步等待回答“为什么 MRI 与 mask 文件数相同，仍必须逐个核对对应文件名”。</s>用户现已回答：“因为数量相同不代表文件一一对应，仍可能有缺失或错配，需要核对病例、时间点和切片编号，确保每张 MRI 对应正确的 mask。”Codex 核对为正确，确认数量与逐名对应的区别。以上扫描与自动检查由 Codex 完成，不记录为用户已亲自核查全量数据。</span>
- <span style="color: purple;">Git 与停止位置：开始本步时最新提交为 bc8a0e4cc57a5e8298d1a2ae390f7bf309523796；仅提交实际数据辅助函数、新文件名检查脚本和带标记说明，不提交数据清单或数据文件，实际新 hash／时间／作者以 git log 为准。与报告对应的是数据配对方法及检查证据；尚无患者划分、补边、模型或训练。到此停止，等待用户反馈。</span>

### <span style="color: purple;">审计训练／验证的 case 分组交集（2026-10-25）</span>

- <span style="color: purple;">本步问题：避免把同一分组的不同切片或时间点分到训练与验证两侧。Codex 在 dataset.py 添加 patient_ids(pairs)，严格匹配 case_数字_week_数字_slice_数字.nii.gz 的完整名称，只提取 case 字段并转为整数加入集合。同编号不同周数／切片归为同组，前导零不产生新组，格式异常直接报错，不静默跳过。</span>
- <span style="color: purple;">标识边界：本步以文件名中数字 case 编号作为患者分组代理，尚未核对原始受试者身份映射。MRI/mask 配对要求 case／week／slice 全部一致；患者分组独立性只按 case 判断，不把 week 或 slice 编入分组键。</span>
- <span style="color: purple;">实际运行：扩展文件名检查脚本，使用既有 collect_pairs 取得训练和验证目录清单，形成 train_ids 与 validation_ids，再用集合交集检查重叠。若交集非空则报告编号并报错，本步不会自动重划分或移动文件。</span>
- <span style="color: purple;">Codex 实际输出：训练路径对 11460、Train case groups: 31；Validation filename pairs: 660、Validation case groups: 4；Shared case IDs: []。固定参考 case_004 对应分组 4，核查其只在训练编号集合。按上述键，两侧没有 case 分组交叉；没有把空交集写成全部无泄漏的证明。</span>
- <span style="color: purple;">Codex 自动核查：所有训练／验证 MRI 名均能按严格格式解析；临时阻断 nib.load 时审计仍成功，确认未读取图像内容；未扫描测试文件名，也未修改数据目录或现有划分。单样本 Dataset/DataLoader 脚本仍保持原样。</span>
- <span style="color: purple;">Codex 构造的解析核查：仅使用内存中的假设路径，训练 case_004_week_0_slice_12 与验证 case_4_week_12_slice_30 都识别为组 4，能检测交集；非法 case 编号报 ValueError。检查通过。该构造例不是真实验证文件，不是临床实验或模型结果。</span>
- <span style="color: purple;">用户理解状态：文件数相同仍需逐名核查已回答正确；<s>本步等待回答“假设固定 case_004_week_0_slice_12 仍在训练侧，而 case_004_week_12_slice_30 放到验证侧，能否通过按患者分组独立性检查，为什么”。</s>用户现已回答：“不能，因为 case 编号都是 004，即使 week 和 slice 不同，也属于同一患者分组，不能跨训练集和验证集。”Codex 核对为正确，确认按当前 case 分组规则保持独立这一点。以上审计由 Codex 执行，不记录为用户已亲自运行或已确认真实患者身份映射。</span>
- <span style="color: purple;">Git 与停止位置：开始本步时最新提交为 4681dceccf86debc069d6603a37f82032be612f4；只提交实际分组辅助函数、检查脚本和带标记说明，不提交患者清单或数据文件，实际新 hash／时间／作者以 git log 为准。与报告对应的是按病例分组的训练／验证边界及数据泄漏检查证据；尚未做真实身份映射、全量像素检查、补边、模型或训练。到此停止，等待用户反馈。</span>

### <span style="color: purple;">完整训练路径清单接入 Dataset，仍只核查参考一批（2026-10-25）</span>

- <span style="color: purple;">本步问题：让 Dataset 保存已核对的完整训练路径清单，同时继续用固定 MRI 核查读取结果。Codex 仅改检查脚本：collect_pairs 取得训练清单，传给 HipMRIPairDataset；用 training_pairs.index((image_path, mask_path)) 找到固定参考切片的位置，不存在时会报错，不自动改取其他切片。</span>
- <span style="color: purple;">取样范围：命名为 reference_loader，使用 batch_size=1、sampler=[reference_index]、num_workers=0，仅选择这一条清单索引。没有把它称作完整训练 loader 或已遍历一个 epoch，也没有在构造 Dataset 时读取 11460 张图像。</span>
- <span style="color: purple;">Codex 实际输出：Dataset samples: 11460；Reference list index: 4；Reference loader batches: 1；MRI batch shape: (1, 1, 256, 128)；Mask batch shape: (1, 256, 128)。固定参考仍为 case_004_week_0_slice_12 与对应 mask；图像范围 0.0～1.0、float32，mask 为 int64、标签 [0, 1, 2, 3]。</span>
- <span style="color: purple;">编号解释：reference_index 是排序路径清单中的零起始位置，4 表示第 5 条记录；文件名中的 case_004 是分组编号。两者本次数值相同只是巧合，sampler 接受位置索引而不是 case 编号，位置会随清单顺序变化而变化。</span>
- <span style="color: purple;">Codex 一致性核查：与本重建仓库上一提交的单样本流程比较，normalized_image、mask_tensor、image_batch、mask_batch 四个 tensor 的逐点值／dtype／device 均保持一致，Dataset 中路径数为 11460，参考 loader 长度为 1，索引处确实是固定路径对。</span>
- <span style="color: purple;">Codex 读取范围核查：只在单独构造与运行参考 loader 的范围内计数。完整 Dataset、loader 和 iterator 构造均未读取 NIfTI；第一次 next 恰好读取固定 MRI 和 mask 两个路径，随后同一迭代器结束且未增加读取。原图预览和前后版本比较会重复读取同一对文件，因此不把整个核查进程描述成总共只读两次。</span>
- <span style="color: purple;">当前限制与用户理解：case 分组独立性已回答正确；本步等待回答“若以后参考切片在清单中的位置变为 7，而 case 编号仍为 004，sampler 应选哪个数字，为什么”。7 是理解题假设，本次真实位置仍是 4。其余训练切片的内容尚未逐个读取验证；以上运行由 Codex 执行。</span>
- <span style="color: purple;">Git 与停止位置：开始本步时最新提交为 b0f914effb89d241640470c992bd619125a37c3a；只提交实际检查脚本及带标记说明，不提交完整路径清单或数据，实际新 hash／时间／作者以 git log 为准。与报告对应的是完整清单的 Dataset 接口和固定参考 batch 的运行证据；未改划分，未做全量像素检查、补边、模型或训练。到此停止，等待用户反馈。</span>

## <span style="color: purple;">协作粒度调整：从本里程碑开始</span>

<span style="color: purple;">用户指出此前拆分过细，要求按真实功能里程碑推进。已有14次真实提交全部保留，不合并、重写或包装成更早的开发历史。以后每组功能完成代码、必要检查和整体讲解后提交，不再按单个方法／一行代码生成提交或强制理解题。此前未回答的 sampler 索引题保持未回答状态。</span>

<table style="color: purple;">
<tr><th>里程碑</th><th>提交应体现的真实工作</th></tr>
<tr><td>读取并配对 MRI／mask</td><td>数据读取、逐名配对与检查</td></tr>
<tr><td>归一化、补边和有效区域</td><td>完整预处理接口、批次整理及实际检查结果</td></tr>
<tr><td>baseline U-Net</td><td>模型及最小训练流程</td></tr>
<tr><td>Improved U-Net</td><td>新增模块、接入过程及验证</td></tr>
<tr><td>发现并修复问题</td><td>实际错误、修改原因和验证；不制造故障记录</td></tr>
<tr><td>公平实验与报告</td><td>验证集选模型、冻结后安排有效评估边界、结果分析；不称旧测试集为未见盲测</td></tr>
</table>

<span style="color: purple;">本轮仅推进预处理里程碑；baseline、Improved 模型和实验留在各自后续里程碑。实际 tutor check-off 状态仍未完成，重新实现不保证 originality hurdle 通过。</span>

## <span style="color: purple;">预处理里程碑：接口与设计</span>

<span style="color: purple;">归一化函数此前已在真实提交 3fa20d9 中形成；本次复用该实现并补齐补边、有效区域、混合尺寸 batch 与恢复原尺寸。以下是本实现的选择，不写成课程指定方案或已验证的最优 MRI 方案。</span>

- <span style="color: purple;">顺序：先对每张 MRI 独立做 min-max 归一化，再向下／向右补到 16 的倍数，不缩放、不转置原始区域。16 为后续四次 2 倍下采样的当前架构规划，可通过参数修改；不是由测试集表现选出的值。常量图归一化为零，非有限数值或非有限强度跨度报错。</span>
- <span style="color: purple;">原始 mask 必须是有限、非负整数类别编号；不做强度归一化或重编码。原始负标签（包括 -100）会报错，不能将数据问题默认为补边。</span>
- <span style="color: purple;">补边规则：image=0；target=-100（IGNORE_INDEX）；valid_mask=False。所有原始像素的 valid_mask=True，包括背景类别0、黑色像素及常量图。这一有效区域不是器官前景掩码。</span>
- <span style="color: purple;">新的单样本接口是字典：image 为 float32 [1,Hpad,Wpad]；target 为 int64 [Hpad,Wpad]；valid_mask 为 bool [Hpad,Wpad]；original_size 保存补边前 (H,W)。原先的二值 tuple 接口已在本次真实代码修改中替换，历史讲解作为当时状态保留。</span>
- <span style="color: purple;">collate_padded 将混合尺寸样本继续补到本批最大尺寸，并保留每个样本已有 valid_mask；batch 返回 image、target、valid_mask、original_sizes。不能把样本先前补过的区域重新标为有效。crop_to_original 按最后两维裁回原尺寸，不插值；valid_pixels 只选有效位置供后续指标使用。</span>
- <span style="color: purple;">后续损失与指标契约：CE 必须使用 ignore_index=-100；Dice／IoU 必须排除 valid_mask=False 的位置，不能直接对含 -100 的 target 做 one-hot。本次仅用构造 logits 验证 CE 忽略行为，没有新增模型、训练或真实 Dice／IoU 成绩。</span>
- <span style="color: purple;">当前调用链只接收本项目 preprocess_pair 生成的样本字典；collate 和有效像素函数信任上游的部分 rank／device／元数据约定。若接入其他数据源，须重新核查接口，不能扩大为任意输入均已覆盖。</span>

### <span style="color: purple;">本次可复现命令（从独立仓库根目录运行）</span>

<span style="color: purple;">下面新增的是可执行命令示例，不把彩色 HTML 写进命令，以保持可直接运行；变更由 Git diff 展示。</span>

```powershell
$python = '..\..\recognition\hipmri_2d_improved_unet\.venv\Scripts\python.exe'
$env:PYTHONDONTWRITEBYTECODE = '1'
& $python -B -m unittest discover -s recognition/hipmri_2d_improved_unet/tests -v
& $python -B recognition/hipmri_2d_improved_unet/audit_preprocessing.py
$env:MPLBACKEND = 'Agg'
$env:MPLCONFIGDIR = Join-Path $PWD 'outputs/.matplotlib'
& $python -B recognition/hipmri_2d_improved_unet/inspect_training_pair.py
```

<span style="color: purple;">全量审计仅处理训练与验证；带 --limit 的试跑会被标为 passed_limited，不能当作完整检查。原始机器报告保存在忽略的 outputs/；本里程碑提交另保存不含本机数据路径或数据文件的汇总证据。构造测试、真实数据审计与用户理解分别记录。</span>

### <span style="color: purple;">预处理里程碑完成记录（2026-10-25）</span>

- <span style="color: purple;">实际改动：归一化后补边、valid_mask／original_size、混合尺寸 collate、有效像素选择及裁回原尺寸均已接入 Dataset 和参考 DataLoader。新增可复现 unittest 与仅训练／验证的流式 audit。已有14次真实提交未改写；本组完成后再产生一次里程碑提交，实际 hash／时间／作者以 git log 为准，开始本组时 HEAD 为 502ef03480ccee30bc4e3d9842aa5342d7e0077c。</span>
- <span style="color: purple;">构造与集成检查：12项 unittest 全部通过、0项跳过。其中构造检查验证17×19补至32×32、323个有效像素、701个补边像素；全背景／常量图仍保留原始有效像素；非法输入拒绝；混合尺寸二次补边不覆盖 valid；crop 与原标签相等；改变 padding 处 logits／预测不改变忽略补边的 CE 或有效像素选择。构造 logits 不属于模型训练或真实分割成绩。</span>
- <span style="color: purple;">全量真实数据审计：单次完整运行总耗时320.898秒；训练11460/11460、验证660/660路径对均通过，0错误，all_pairs_attempted=true，status=passed_full。两侧实际标签集合均为[0,1,2,3,4,5]，归一化汇总范围[0,1]；case分组31/4、交集为空，仍是文件名代理核查。没有读取测试集或用已知旧测试结果调参。</span>
- <span style="color: purple;">实际尺寸发现：训练256×128为11400对、256×144为60对；验证660对均256×128。两种真实原尺寸均能整除16，所以逐图补边数量为0；不能将构造的17×19补边例写成真实 MRI 数据分布。训练有效像素375767040、验证21626880，逐图新增padding像素均0。</span>
- <span style="color: purple;">真实混合batch核查：固定参考case_004_week_0_slice_12(256×128)与case_019_week_1_slice_0(256×144)组成一批。默认collate在本次对照核查中实际报尺寸不一致；自定义collate得到[2,1,256,144]，两条valid像素数为[32768,36864]，补边像素数[4096,0]；padding target=-100、image=0、裁回后target逐点等于原NIfTI标签。该检查已加入可复现的本地数据集成测试；缺少本地数据时会明确skip。本轮没有将其包装成此前训练曾失败的历史。</span>
- <span style="color: purple;">固定参考：原始256×128、32768个有效像素、0补边，图像范围仍0～1，参考图标签仍[0,1,2,3]；已查看预览。包含该样本的完整 Dataset 仍按需读取，未开始训练。混合batch所用第二张图只用于本里程碑的数据接口核查。</span>
- <span style="color: purple;">证据：evidence/preprocessing_audit.json 保存去掉本机绝对数据路径的汇总、真实混合batch结果和源文件SHA256，不含图像／tensor／完整患者清单。原始机器报告 outputs/preprocessing_audit.json、限量试跑及预览仍留在忽略目录；限量试跑未被当作全量结果。审计源码在完整运行开始后未修改。</span>
- <span style="color: purple;">证据边界：所有代码编写、自动检查、全量审计和本次提交均由 Codex 执行。用户本轮只调整了协作粒度，尚未确认已理解整组预处理，不记为亲自运行或通过原创性审查。审计检查的是处理契约，不独立证明真实身份映射、物理空间对应或标注医学准确度，也不构成模型性能结果。</span>
- <span style="color: purple;">当前里程碑到此完成；下一组是 baseline U-Net 及最小训练流程，本轮没有生成或运行模型、优化器、训练与测试评估。原项目、原PR、原历史不变，实际 tutor check-off 仍未完成。</span>

## <span style="color: purple;">Baseline U-Net 与最小训练流程里程碑（2026-10-25）</span>

<span style="color: purple;">本组按用户指定的完整功能里程碑推进；只实现 baseline，不提前添加 Improved U-Net 或测试集评估。读取训练／验证文件夹，延续相同逐图归一化、补边、有效区域与 case 分组边界。此前15次真实提交全部保留。</span>

### <span style="color: purple;">实现与整体流程</span>

- <span style="color: purple;">modules.py 只依赖 PyTorch：四次2×下采样、双3×3卷积＋ReLU、转置卷积上采样、同级skip concat、1×1输出6类原始logits。参数量1,940,902。没有预训练权重、BN、dropout、residual、attention或deep supervision。</span>
- <span style="color: purple;">拓扑依据：[U-Net原论文](https://arxiv.org/abs/1505.04597)。原文使用valid卷积／skip裁剪和64起始通道；本项目采用same-padding和base_channels=16以匹配既有尺寸管线及当前资源，Adam也是本项目选择，不称为逐细节复现原论文。</span>
- <span style="color: purple;">最新任务书第5页要求basic U-Net baseline与one-hot多通道标注，第13页要求训练保存、曲线与加载推理。本组实际接入这些接口；未据此声称最终提交、患者真实身份映射、医学准确度或 originality hurdle 已通过。</span>
- <span style="color: purple;">losses.py 在训练时把 class-ID target 安全编码为 [B,6,H,W] one-hot：先将无效的-100替为安全0，再编码并将无效位置所有通道清零。实际CE按 one_hot×log_softmax 对有效像素求平均；构造检查证明值与梯度等价于 F.cross_entropy(ignore_index=-100)。没有加入Dice loss，原始mask不改写。</span>
- <span style="color: purple;">train.py 的主线：DataLoader → UNet logits → 有效区域CE → zero_grad／backward／Adam step；每步检查有限非零梯度。验证切到eval并关闭梯度，不执行optimizer step。训练CE为各batch更新前的在线统计；验证为epoch结束后固定模型的整集统计，二者不混称。</span>
- <span style="color: purple;">metrics.py 按整个split累计 int64 confusion matrix，然后计算每类Dice／IoU；不平均各batch的Dice。类别在预测与target均缺失时返回None并排除macro；只有预测、没有target的类别计0。macro明确排除数字ID0，这一数值约定不替代组织标签映射。</span>
- <span style="color: purple;">最新任务书第17页列出组织名称但未给出0…5对应关系，因此所有结果只标class ID。尤其不能把ID1的Dice当作prostate Dice，更不能据此宣称达到Normal模型的最终指标。</span>
- <span style="color: purple;">predict.py 只提供training／validation两种split，加载本次baseline checkpoint，eval＋无梯度推理，裁回原尺寸，输出参考／预测对照图。没有test选项，也未实现Improved模型。</span>

<span style="color: purple;">固定参考MRI的张量链：image [1,1,256,128] → encoder通道16/32/64/128 → bottleneck [1,256,16,8] → decoder＋skip → logits [1,6,256,128]。one-hot target同为[1,6,256,128]；每个原始像素只有正确类别通道为1，padding通道全0。logits是分数，不在模型末端重复做softmax。</span>

### <span style="color: purple;">真实运行：固定的小规模功能演示</span>

- <span style="color: purple;">运行前记录计划于 evidence/baseline_run_plan.json：seed=3710，Adam lr=0.001，batch_size=4，base16，2轮；从11460训练路径中固定随机选64个（包含case_004_week_0_slice_12），每轮完整遍历这64个样本，覆盖20个case分组；每轮验证全部660个验证样本。完整训练／验证仍为31／4个case代理分组、交集为空。未进行超参数搜索或按结果追加训练。</span>
- <span style="color: purple;">这两轮是 selected-subset / smoke epochs，不是对11460个训练样本完成两轮训练，也不是正式公平baseline成绩。后续正式实验必须为baseline和Improved另定相同训练／验证协议。</span>

<table style="color: purple;">
<tr><th>64样本smoke轮次</th><th>在线训练CE</th><th>全660验证CE</th><th>验证ID1 Dice</th><th>验证macro Dice（排除ID0）</th></tr>
<tr><td>1</td><td>1.530331</td><td>1.058691</td><td>0.825835</td><td>0.165167</td></tr>
<tr><td>2</td><td>1.056190</td><td>0.921908</td><td>0.827342</td><td>0.165468</td></tr>
</table>

- <span style="color: purple;">实际发生32次Adam更新；固定训练参考CE由1.706104降至0.877492，首个参数张量最大变化0.029494。每轮验证统计21626880个有效像素。验证ID0、2、3、4、5的Dice均为0；预测主要落在ID1，少数类别尚未学会，不能只凭CE下降声称分割有效或满足最终要求。</span>
- <span style="color: purple;">按预先规定的最小验证CE选择第2轮best checkpoint；重新加载后的参考logits最大差值为0，独立predict入口得到同一参考CE 0.877492、logits [1,6,256,128]并恢复256×128输出。训练参考图属于训练样本，不是独立评估。</span>
- <span style="color: purple;">CUDA运行：NVIDIA GeForce RTX4070Ti；记录的训练／验证及收尾流程用时9.845秒。PyTorch峰值allocated=171819008 bytes、reserved=209715200 bytes；该进程峰值包含checkpoint恢复等流程，不是纯训练峰值或整卡VRAM。记录了软件版本与seed；没有验证跨环境位级一致性。</span>
- <span style="color: purple;">34项自动检查全部通过、0跳过：包括既有预处理、模型形状／梯度／权重恢复、手算Dice/IoU与缺失类别、one-hot CE值及梯度等价、padding排除、训练实际更新与验证无更新。构造数据检查不是额外MRI实验；全部检查由Codex执行。</span>

### <span style="color: purple;">复现与证据</span>

<span style="color: purple;">以下新增命令块保持可执行，颜色不嵌入命令；由Git diff显示新增。所有输出目录必须是新目录，以保留既有运行记录。</span>

```powershell
$python = '..\..\recognition\hipmri_2d_improved_unet\.venv\Scripts\python.exe'
$env:PYTHONDONTWRITEBYTECODE = '1'
& $python -B -m unittest discover -s recognition/hipmri_2d_improved_unet/tests -v
& $python -B recognition/hipmri_2d_improved_unet/train.py --output-dir outputs/baseline_reproduce --epochs 2 --batch-size 4 --base-channels 16 --num-classes 6 --lr 0.001 --seed 3710 --train-limit 64 --device cuda
& $python -B recognition/hipmri_2d_improved_unet/predict.py --checkpoint outputs/baseline_reproduce/best.pt --split training --filename case_004_week_0_slice_12.nii.gz --output-dir outputs/baseline_reference_reproduce --device cuda
```

<span style="color: purple;">evidence/baseline_smoke.json 记录完整各轮汇总、样本选择摘要、源文件SHA256和checkpoint摘要；baseline_reference.json 记录固定训练样本推理；baseline_training_curves.png 是聚合曲线。best.pt／last.pt、原始运行JSON和包含MRI的预测图留在忽略的outputs/，不提交模型或数据。代码基于当前重建项目与公开基础架构实现，没有读取旧项目源码、旧权重或旧实验结果作为本次新工作。</span>

<span style="color: purple;">本组从 e76fa43e5b9406ce7f342cec74a17724d9c0843a 开始，仅提交实际baseline实现、检查、文档和汇总证据，实际新hash／时间／作者以git log为准。用户授权执行本组，但尚未反馈已理解全部代码，不能写成用户亲自运行、独立实现或通过check-off。实际tutor check-off仍未完成。本组没有实现Improved U-Net、读取测试集、执行最终评估或发布PR。</span>

## <span style="color: purple;">Improved U-Net 模块与共用流程接入里程碑（2026-10-25）</span>

<span style="color: purple;">本组从7ae1584d97f0b6b60825c54bd0310b6c18ec586f开始，按一个完整功能里程碑推进。任务书第6页的2D Improved U-Net指向Ref[2]；第20页对应Isensee等人的2018年论文 <a href="https://arxiv.org/abs/1802.10508">Brain Tumor Segmentation and Radiomics Survival Prediction: Contribution to the BRATS 2017 Challenge</a>。本模型基于其§2.1／Figure 1做2D改编，保留baseline另作选择。</span>

### <span style="color: purple;">新增模块及一次前向传播</span>

<table style="color: purple;">
<tr><th>部分</th><th>baseline</th><th>本组Improved实现</th></tr>
<tr><td>编码特征</td><td>双3×3卷积＋ReLU</td><td>ResidualContext：x＋F(x)，F为两个预激活3×3卷积，中间Dropout2d(0.3)</td></tr>
<tr><td>预激活</td><td>卷积后ReLU</td><td>PreActConv：InstanceNorm2d → LeakyReLU(0.01) → 卷积</td></tr>
<tr><td>下采样</td><td>MaxPool2d</td><td>3×3 stride=2卷积</td></tr>
<tr><td>上采样</td><td>转置卷积</td><td>NearestUpConv：nearest放大2倍，再3×3卷积减半通道</td></tr>
<tr><td>同级skip融合</td><td>concat后双卷积</td><td>LocalizationBlock：concat后3×3保持拼接通道，再1×1减半通道</td></tr>
<tr><td>分类输出</td><td>最末层一个1×1分类头</td><td>quarter／half／full三个1×1分类头，逐级nearest上采样并相加，输出单个logits tensor</td></tr>
</table>

<span style="color: purple;">残差相加要求输入与F(x)形状一致。直通分支保留x，卷积分支学习修正量；当分支卷积全部置零时，检查确认输出严格等于x。InstanceNorm对每张图每个通道的空间位置计算统计量，affine参数可学习，未维护running statistics；Dropout2d训练时随机置零整张特征通道，eval时关闭。以上机制提供不同的表示与优化路径，效果仍须由后续实验判断。</span>

<span style="color: purple;">以固定MRI为例：输入[B,1,256,128] → 五尺度编码通道16／32／64／128／256，对应空间256×128、128×64、64×32、32×16、16×8 → 解码至原尺寸。第一次解码把256通道上采样并映射为128通道，与同级128通道skip拼成256通道；localization先保留256，再经1×1降至128。后续各级按相同方式接入。</span>

<span style="color: purple;">三个分类头分别产生[B,6,64,32]、[B,6,128,64]、[B,6,256,128]。先将quarter放大与half相加，再放大与full相加。最终[B,6,256,128]直接交给既有one-hot CE；同一个loss可以沿三个分类头反向传播到不同深度，检查确认三头均得到非零梯度。这里没有额外auxiliary loss，末端不提前softmax。</span>

<span style="color: purple;">明确的改编选择：3D空间操作改为2D；使用channel-wise Dropout2d、affine InstanceNorm与三个分类头；base16与原baseline共用。论文还包含特定归一化、Dice loss、数据增强、学习率计划和长训练方案；本组保持既有逐片min-max、有效区域CE与smoke优化设置，未复现整套论文训练配方。默认Improved参数量3,190,194，baseline仍为1,940,902；两者容量不同。</span>

<span style="color: purple;">输入仍须为16的倍数；InstanceNorm还要求最深层至少两个空间元素，16×16会得到1×1并被明确拒绝，16×32和32×32可用。当前真实MRI尺寸满足约束。valid_mask只限制loss与指标计数，卷积与InstanceNorm仍会看到图像补边值，因此不声称混合batch补边对预测完全无影响。</span>

### <span style="color: purple;">保留与接入</span>

- <span style="color: purple;">modules.py的原DoubleConv／UNet类源码逐字保留，新增build_model(name, **config)选择baseline_unet或improved_unet。train.py新增--model，默认仍为baseline。两种模型均返回同形状raw logits，后面的训练步骤无需分叉。</span>
- <span style="color: purple;">dataset.py、losses.py、metrics.py与上一提交字节一致。seed_everything、manifest_hash、select_training_pairs、move_batch、run_epoch、reference_probe六个共用函数源码保持一致；归一化、补边、valid区域、one-hot CE、整集confusion／Dice／IoU和验证禁用更新的规则共用。</span>
- <span style="color: purple;">checkpoint保存model名称和原有三个model_config字段；训练恢复最佳权重和predict入口均据此选择模型。旧baseline checkpoint无需转换，已用真实旧文件通过新入口恢复。预测仍只提供training／validation；本组未读取测试文件名、像素或指标。</span>
- <span style="color: purple;">真实训练前复核发现localization初稿把通道减半放在3×3，而论文描述由1×1负责。已改成3×3保持拼接通道、1×1减半，并加入结构检查后再开始运行。此为本轮实际发现和修正的实现偏差，没有包装成此前发生的训练故障。</span>

### <span style="color: purple;">实际运行与验证结果</span>

<span style="color: purple;">evidence/improved_run_plan.json在两次真实运行前记录设置和源文件SHA256。先跑baseline回归，再跑Improved；二者均为seed3710、同一固定64训练样本、2轮、batch4、base16、Adam lr0.001，32次更新；每轮完整验证<s>660例</s>660个验证切片样本（4个case代理组），按最小验证CE保存best。样本清单摘要、训练／验证设置已逐项核对一致，无额外调参或追加训练。同一seed不表示不同架构拥有相同初始权重。</span>

<table style="color: purple;">
<tr><th>模型／轮次</th><th>在线训练CE</th><th>全660验证CE</th><th>验证macro Dice（排除ID0）</th></tr>
<tr><td>baseline回归／1</td><td>1.530331</td><td>1.058691</td><td>0.165167</td></tr>
<tr><td>baseline回归／2</td><td>1.056190</td><td>0.921908</td><td>0.165468</td></tr>
<tr><td>Improved／1</td><td>0.736550</td><td>0.447986</td><td>0.273869</td></tr>
<tr><td>Improved／2</td><td>0.353347</td><td>0.385807</td><td>0.339030</td></tr>
</table>

- <span style="color: purple;">baseline回归：与上一里程碑的样本选择、各轮loss／指标完全相同，最佳checkpoint全部参数tensor逐值相等。旧baseline checkpoint经过当前predict入口得到参考CE0.877492及相同指标，证明新增入口保留了该baseline行为。</span>
- <span style="color: purple;">Improved第2轮ID0…5 Dice依次为0.969482、0.904251、0.428347、0.362553、0、0；每轮统计21626880个验证有效像素。<s>ID4／ID5仍未学会</s>ID4／ID5的验证Dice仍为0；组织编号映射尚未确认，不能把任意ID的分数称为某组织达标结果。</span>
- <span style="color: purple;">Improved所有训练步梯度有限且非零，首个参数张量最大变化0.015980；固定训练参考CE从1.877008降至0.249754。最小验证CE选择第2轮，重新加载后参考logits最大差值0；独立predict入口同样得到CE0.249754和原尺寸256×128输出。</span>
- <span style="color: purple;">47项检查全部通过、0跳过（原34项＋新增13项）：残差直通、多尺度输出／融合、三头梯度、参数更新、恢复一致性、异常输入，以及两模型共用混合尺寸补边batch、训练更新、eval／无梯度验证无状态变化、旧baseline权重兼容。构造检查、真实MRI smoke与用户理解状态分别记录；本轮全部由Codex执行。</span>
- <span style="color: purple;">已查看Improved聚合曲线及固定训练图预测：预测中出现ID2／ID3区域，但ID2存在碎片和遗漏，边界也有偏差；这是训练图外观检查，不是独立评估或医学判断。预测图和权重留在忽略的outputs/，仅聚合曲线纳入Git。</span>
- <span style="color: purple;">Improved训练／验证及收尾计时11.926秒；RTX4070Ti上PyTorch峰值allocated529318400 bytes、reserved658505728 bytes，包含checkpoint恢复。没有将其视为纯训练显存、整卡占用或严格速度比较。</span>

<span style="color: purple;">这组smoke验证了模块与流程接通；64个样本的2轮结果不能证明Improved最终优于baseline，也不能归因于某一个模块。正式公平实验、消融、充分训练和最终测试尚未开展；本组没有做测试集评估。</span>

### <span style="color: purple;">复现与提交边界</span>

<span style="color: purple;">在本重建仓库根目录执行；命令块保持可执行，由Git diff显示新增。目录必须取新名称。</span>

```powershell
$python = '..\..\recognition\hipmri_2d_improved_unet\.venv\Scripts\python.exe'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:MPLBACKEND = 'Agg'
& $python -B -m unittest discover -s recognition/hipmri_2d_improved_unet/tests -v
& $python -B recognition/hipmri_2d_improved_unet/train.py --model baseline_unet --output-dir outputs/baseline_regression_reproduce --epochs 2 --batch-size 4 --base-channels 16 --num-classes 6 --lr 0.001 --seed 3710 --train-limit 64 --device cuda
& $python -B recognition/hipmri_2d_improved_unet/train.py --model improved_unet --output-dir outputs/improved_reproduce --epochs 2 --batch-size 4 --base-channels 16 --num-classes 6 --lr 0.001 --seed 3710 --train-limit 64 --device cuda
& $python -B recognition/hipmri_2d_improved_unet/predict.py --checkpoint outputs/improved_reproduce/best.pt --split training --filename case_004_week_0_slice_12.nii.gz --output-dir outputs/improved_reference_reproduce --device cuda
```

<span style="color: purple;">evidence/improved_smoke.json保存各轮结果、预运行计划关联、源文件与权重摘要、检查和外观核查；improved_reference.json保存固定训练图推理；improved_training_curves.png为聚合曲线；baseline_regression.json记录保留行为的验证。旧baseline及预处理证据原样保留，权重、MRI、逐像素预测不纳入Git。</span>

<span style="color: purple;">已有16次真实提交不改写，本组完成后增加一次实际里程碑提交，实际hash／时间／操作者以git log为准。未修改旧项目、旧PR或远程仓库。用户尚未确认理解整组Improved代码，实际tutor check-off与originality hurdle状态不因自动执行而改变；也不能声称旧测试结果此前从未被接触。</span>

## <span style="color: purple;">正式实验前：空间检查修复、标签来源与整体核查（2026-10-25）</span>

<span style="color: purple;">本轮从719b02616db73d9f14d78ae28a1e6a5c95ceda87开始。用户要求先补空间检查、核实标签来源，再核查整体流程；明确确认后才正式全量训练。以下是本次新检查，不回写成此前smoke已经检查过的内容。原预处理、baseline及Improved smoke证据保留。</span>

### <span style="color: purple;">实际问题、修复与补充审计</span>

<span style="color: purple;">此前load_pair直接取get_fdata数组，只检查二维shape；同shape不保证空间信息一致。新增validate_pair_geometry先保留两个NIfTI对象，检查非空二维shape匹配、两侧选出的.affine为有限4×4矩阵，再用绝对atol=1e-5、rtol=0比较。相对容差设0，避免很大的坐标原点掩盖平移差异；容差以Affine自身坐标单位计，不擅自解释为毫米或临床距离。异常在读取像素数组前报错，不自动对齐、重采样或修改mask。</span>

<span style="color: purple;">新增6项构造检查：正常匹配；同8×4 shape但mask平移100时拒绝；两侧NaN／±Inf拒绝；绝对容差内外边界；大原点下仍拒绝0.1差异；shape不同拒绝。错误几何检查时阻断get_fdata，确认先检查头信息。原mask数值测试由缺少头信息的SimpleNamespace改为真实Nifti1Image，保留非法mask应拒绝的断言。完整53项检查通过、0跳过，均由Codex执行。</span>

<span style="color: purple;">新增audit_geometry.py只检查训练／验证NIfTI头信息，没有materialize像素数组。实际训练11460／11460、验证660／660对全部通过，错误0，最大Affine差异0，用时24.482秒；31／4个case代理组交集为空。所有12120对都是identity Affine、qform_code=0／sform_code=2、声明空间单位unknown。它证明当前导出头信息一致，不能恢复原始3D物理坐标，也不能独立证明解剖对齐、单位真实性或医学标注正确；检查的是NiBabel选出的.affine，不是完整qform／sform来源审查。</span>

<span style="color: purple;">evidence/geometry_audit.json保存本次范围、时间、矩阵／单位统计、源码hash及检查结果。最大差异统计通过的pair；本次全部通过，因此覆盖全量。旧preprocessing_audit.json没有被改成已检查Affine；未来预处理审计经修复后的load_pair也会先执行该检查。</span>

### <span style="color: purple;">标签ID：原始来源已确认，派生保留ID仍是假设</span>

<span style="color: purple;">2026-10-25实际核实了CSIRO <a href="https://doi.org/10.25919/45t8-p065">数据集DOI</a>、<a href="https://data.csiro.au/dap/ws/v2/collections/52549">version 2 collection API</a>及<a href="https://data.csiro.au/dap/ws/v2/collections/52549/support/5034">BriefDataDescription.txt</a>。支持文件HTTP 200、695 bytes，SHA256为dc3a99204684ced859872d79a75707af3c0ad31d00f5f3213063ce5e30727ee6，与本地来源备份字节一致。原始说明明确给出下表，不由颜色或模型表现猜测。</span>

<table style="color: purple;">
<tr><th>原始ID</th><th>提供方名称</th><th>中文工作名称</th></tr>
<tr><td>0</td><td>Background</td><td>背景</td></tr>
<tr><td>1</td><td>Body</td><td>身体区域</td></tr>
<tr><td>2</td><td>Bones</td><td>骨骼</td></tr>
<tr><td>3</td><td>Bladder</td><td>膀胱</td></tr>
<tr><td>4</td><td>Rectum</td><td>直肠</td></tr>
<tr><td>5</td><td>Prostate</td><td>前列腺，拟定主要目标</td></tr>
</table>

<span style="color: purple;">课程任务书v2.5第17页把keras_slices_data列为同一HipMRI_Study_open的2D数据，旁列3D MRI／labels与器官名；本地download_HipMRI_2D.cmd第21行只是从课程目录scp复制，没有本地重编码步骤。但脚本不证明成功传输／完整性；已检查材料未提供3D→2D导出代码、发布者未重编码声明或逐文件原体数据对照。标签集合0…5本身不能证明未重编码。</span>

<span style="color: purple;">新增label_schema.json区分source_raw_mapping_verified=true与derivative_no_remap_verified=false，保持六类和原mask数值。ID5是有原始来源依据的工作目标；解释为当前派生数据的前列腺仍依赖“导出保留原ID”假设。后续用户确认表示知情接受工作假设，不会把假设变成来源证明。旧图继续保留数字ID，应用组织名称时应同时保留该边界。</span>

### <span style="color: purple;">用固定训练MRI核查整条流程</span>

<span style="color: purple;">新增review_pipeline.py只读取固定训练对及本独立仓库现存smoke checkpoint，不创建优化器、不训练。实际报告为evidence/pipeline_review.json。Dataset在该脚本中只有一对，用于核查，不是新的正式训练清单。</span>

<table style="color: purple;">
<tr><th>环节</th><th>固定样本的实际结果／代码含义</th></tr>
<tr><td>1 配对及空间信息</td><td>case_004_week_0_slice_12与seg_004_week_0_slice_12；均256×128，Affine差0、单位unknown。文件名、shape和Affine分别检查。</td></tr>
<tr><td>2 归一化</td><td>MRI原范围0…438，整片min-max后0…1；mask编号不归一化、不改写。</td></tr>
<tr><td>3 补边与有效区域</td><td>256和128均能整除16，当前padding为0；32768个原始像素全部valid，包括ID0。记录original_size用于裁回。</td></tr>
<tr><td>4 Dataset与batch</td><td>Dataset按编号调用load_pair，DataLoader经collate_padded组成image [1,1,256,128]、target [1,256,128]。</td></tr>
<tr><td>5 六类logits</td><td>baseline或Improved均输出[1,6,256,128]；6通道是每个像素的类别分数，类别编号没有亮度倍数关系。</td></tr>
<tr><td>6 One-hot CE与更新</td><td>one-hot同为[1,6,256,128]；真实(row100,col84)标注ID3编码[0,0,0,1,0,0]。CE只对valid像素平均。训练执行zero_grad→forward→loss.backward→Adam.step更新权重，不更新mask；本次review未执行更新，行为由构造测试和原smoke验证。</td></tr>
<tr><td>7 验证与推理</td><td>eval关闭dropout，关闭梯度，不调用backward或optimizer.step；本次两模型state保持不变，logits requires_grad=false。正式验证将遍历全660切片。</td></tr>
<tr><td>8 指标</td><td>先累计整个split有效像素confusion，再算每类Dice=2TP/(2TP+FP+FN)和IoU；不是batch Dice平均，也不是case等权均值。</td></tr>
<tr><td>9 保存／选择／恢复</td><td>原smoke按最小全验证CE选第2轮，checkpoint记录model与配置；factory恢复。新几何检查下baseline参考CE仍0.8774915934，Improved仍0.2497540712，与smoke对应值一致。</td></tr>
<tr><td>10 裁回预测</td><td>对6通道取argmax得类别编号图，按original_size裁回256×128；参考mask逐点编号保持。含MRI预测图仍在忽略的outputs/。</td></tr>
</table>

<span style="color: purple;">本片target中ID0…5像素数依次为[2890,25038,3528,1312,0,0]，没有ID4／5。Improved训练参考macro Dice=0.800043，只平均当前有定义的ID1／2／3；ID4／5因预测和target均缺失返回null。这不能证明目标ID5达标，也不是全验证结果；此前全验证smoke的ID5 Dice仍为0。训练参考、验证集、目标器官与类别macro必须区分。</span>

### <span style="color: purple;">与旧项目的实际差异</span>

<span style="color: purple;">按本轮要求只读比较旧源码，没有复制实现、加载旧权重或读取旧结果／测试文件。旧项目HEAD仍82c794f55bb935cc40f92de990bfcd9165b2361d且工作树干净。以下描述源码差异，不是追加实验。</span>

<table style="color: purple;">
<tr><th>部分</th><th>旧实现</th><th>当前重建</th></tr>
<tr><td>预处理</td><td>正强度p1–p99裁剪缩放；中心补至256×144；float16量化；训练gamma／强度增强</td><td>整片min-max；下／右16倍数及动态batch补边；float32；无增强；本轮才补Affine检查</td></tr>
<tr><td>Loss</td><td>CE＋ID1–5 soft Dice</td><td>共享有效区域one-hot CE</td></tr>
<tr><td>Baseline</td><td>同类五尺度U-Net、1940902参数；显式He／Xavier初始化、内部pad／crop</td><td>1940902参数；PyTorch默认初始化、外部保证16倍数</td></tr>
<tr><td>Improved</td><td>特殊首context／decoder投影、postnorm局部块、普通Dropout；分类头在通道减半前；3206562参数</td><td>统一preactivation模块、Dropout2d；分类头在减半后；3190194参数</td></tr>
<tr><td>主要指标／选模</td><td>volume Dice先按case平均、再case等权的ID5 Dice；按其选best</td><td>全split像素pool Dice／IoU，另报排除ID0的类别macro；按最小验证CE选best</td></tr>
<tr><td>训练控制</td><td>AdamW、AMP、梯度裁剪、ReduceLROnPlateau、early stopping</td><td>Adam、FP32、固定轮数，无这些附加控制</td></tr>
</table>

<span style="color: purple;">旧0.8316／0.8233不能充当新结果，也不能直接与当前macro Dice比较；模型、输入、loss、预算、选模与聚合口径均不同。本轮没有为了得到旧分数而改mask、读取测试或调参。</span>

### <span style="color: purple;">正式公平实验方案：等待明确确认</span>

<span style="color: purple;">完整方案为evidence/formal_experiment_proposal.json，状态awaiting_user_confirmation、executed=false；当前train CLI不读取该JSON，它是可审阅方案，不是已经执行的配置。</span>

<table style="color: purple;">
<tr><th>控制项</th><th>拟定规则，两模型共用</th></tr>
<tr><td>样本／输入</td><td>全部11460训练／660验证切片；31／4个case代理组；相同清单摘要、min-max、16倍数下右补边、动态batch及valid区域规则</td></tr>
<tr><td>优化</td><td>base16、六类；seed3710、batch4、FP32、Adam lr0.001／weight_decay0、one-hot CE；无增强、AMP或scheduler</td></tr>
<tr><td>预算／停止</td><td>每模型20个完整epoch，每轮2865次更新，共57300次；不按验证追加、不early-stop。非有限／错误／OOM则停、保存证据并标incomplete；不能只改一方设置或声称公平比较完成</td></tr>
<tr><td>主要指标</td><td>全验证像素pool的ID5 Dice；仅在派生保留ID假设下称前列腺Dice。另报六类Dice／IoU、macro和CE；不与旧case-balanced口径混用</td></tr>
<tr><td>选模</td><td>沿用最小全验证CE；并列最早轮。主报告ID5与选模CE分开，不事后挑分数更好的轮次</td></tr>
<tr><td>显存</td><td>确认后、正式运行前补并检查分阶段记录：training／validation／checkpoint恢复分别CUDA同步及重置峰值，报告驻留模型／优化器。旧smoke峰值包含恢复，保留原范围</td></tr>
<tr><td>独立推理</td><td>固定合成输入，batch1／4及256×128／256×144、FP32；warmup10后50次同步计时，报median／p95；排除加载、I/O、传输、指标与绘图，无优化器驻留</td></tr>
</table>

<span style="color: purple;">20轮是拟定预算，不保证达标。若需改方案，应在运行前明确并共同应用；未达也如实记录。两模型用训练／验证选定并冻结后，才另行明确后续评估边界；用户和Codex已接触旧测试结果，不能称测试集从未见过或据其调参。本次没有测试评估或PR发布授权。</span>

### <span style="color: purple;">用户核查状态、复现与提交</span>

<span style="color: purple;">53项检查、头信息审计、来源核实与固定图恢复均由Codex完成。用户尚未核对本轮整体流程、回答关键核查或确认正式方案，不能将执行委托写成理解通过。待用户核查：本片没有ID5时macro≈0.8000能否说明前列腺效果；验证为何不能执行backward／optimizer.step。正式训练需明确确认方案及派生ID工作假设；未回复不构成同意。tutor check-off／originality hurdle状态不因自动检查改变。</span>

<span style="color: purple;">以下命令仅检查／头信息审计／既有权重推理，不进行正式训练；输出须用新路径。命令块保持可执行，新增由Git diff显示。</span>

```powershell
$python = '..\..\recognition\hipmri_2d_improved_unet\.venv\Scripts\python.exe'
$env:PYTHONDONTWRITEBYTECODE = '1'
& $python -B -m unittest discover -s recognition/hipmri_2d_improved_unet/tests -v
& $python -B recognition/hipmri_2d_improved_unet/audit_geometry.py --output outputs/geometry_audit_reproduce.json
& $python -B recognition/hipmri_2d_improved_unet/review_pipeline.py --device cuda --output outputs/pipeline_review_reproduce.json
```

<span style="color: purple;">已有17次提交保持；修复、来源配置、核查脚本、检查、证据与待确认方案按本轮实际进度提交一次，真实hash／日期／操作者以git log为准。权重、MRI和含MRI预测图仍在忽略的outputs/；旧项目／PR未修改，新仓库仅本地保存，不倒签或覆盖历史。本轮在整体核查与方案确认处停止，不启动正式全量训练。</span>

## <span style="color: purple;">用户确认与分阶段资源记录就绪（2026-10-26）</span>

<span style="color: purple;">本组从344e1f38a35a888c2c7baa4e493d4a34d28c3c75开始。用户本次回答两个核查点均正确，明确认可方案、接受“课程派生标签保留原ID”的工作假设，并授权由Codex执行资源检查后两模型各20轮训练及本地Git提交，仍不做测试评估。evidence/user_confirmation_20261026.json保存用户原话、日期与原方案摘要；此前proposal和待确认记录作为当时事实保留。该确认不独立证明派生映射、全部代码理解、check-off或originality通过。</span>

<span style="color: purple;">resource_monitor.py新增StageMeasurement上下文：进入CUDA阶段先同步、重置峰值并记录起始allocated／reserved；退出先同步，再记录峰值和结束占用及耗时。CPU的CUDA字段为null。它不改RNG、模型模式、参数或训练公式，不清缓存；body异常继续抛出，失败统计不能伪装成功。</span>

<table style="color: purple;">
<tr><th>阶段</th><th>驻留对象与范围</th></tr>
<tr><td>每轮training</td><td>模型、Adam状态（首次更新后建立）、梯度，以及该轮batch输入／输出／中间激活；统计完整epoch含读取与指标的同步墙钟时间</td></tr>
<tr><td>每轮validation</td><td>同一模型、Adam状态和最后训练步留下的梯度仍驻留；新增验证输入／输出，eval／无梯度／无optimizer更新</td></tr>
<tr><td>checkpoint恢复</td><td>最终训练模型、Adam和梯度仍驻留；另建第二个模型加载best，执行固定训练参考恢复核查。checkpoint先在CPU加载</td></tr>
</table>

<span style="color: purple;">各阶段都记录绝对峰值，不是相对起点的新增量；缓存reserved占用仍计入，不能把它当独立临时需求或整卡VRAM。报告中的兼容peak字段是已测阶段峰值的最大值；不再声称是未测流程的完整进程峰值。旧smoke的“包含恢复”范围原样保留。</span>

<span style="color: purple;">train.py在原共享epoch调用外包裹资源记录，只加批次进度输出，loss／反向／Adam／验证公式保持。--formal-plan会检查用户确认、20轮／batch4／base16／六类／lr0.001／seed3710／CUDA／无train-limit、模型名单、数据清单及源码摘要，任一漂移拒绝。训练主体失败或中断标incomplete；另补setup失败兜底，模型上GPU或参考读取等在主体前失败，也保存新路径下的incomplete报告，不覆盖旧输出。</span>

<span style="color: purple;">67项检查通过、0跳过：在原53项上增加5项资源记录CPU／mock-CUDA检查和9项正式计划／失败记录检查。GPU另以原64样本／2轮设置检查两模型，逐轮loss／指标、参考CE及best权重与各自原smoke逐值一致，新增六个阶段均成功，证据为evidence/resource_checks_20261026.json。这是资源接入回归，不是正式20轮，也不参与最终选模。</span>

<span style="color: purple;">profile_inference.py在独立进程加载checkpoint，释放CPU checkpoint对象后只将模型放到GPU，不构造优化器。使用固定合成FP32输入，batch1／4及256×128／256×144，10次warmup后50次前后同步计时，保存原始ms、median和linear方法p95；只计forward与host启动／同步，排除加载、I/O、传输、指标和绘图。每组合setup前释放闲置cache，warmup cache保留进入测量；此策略不用于训练。FP32指张量类型且无AMP，实际TF32后端设置单独记录。</span>

<span style="color: purple;">推理入口已用构造base2 checkpoint在CPU走完四组合并复算百分位，重复输出明确拒绝；CPU结果不当GPU性能。两模型正式GPU profile在各20轮完成、验证CE选定checkpoint后执行。模型／预处理／loss／指标代码保持；源文件与实际配置会在正式运行前冻结记录，运行过程不因验证分数追加轮数或改参数。</span>

<span style="color: purple;">本组先提交已检查的资源实现、确认记录和回归证据；随后在运行前写入包含此源码提交、文件hash、训练／验证清单hash、批准方案及新输出路径的formal_run_plan_20261026.json。正式结果完成后再按真实进度提交证据。所有运行均由Codex执行；旧项目、旧结果和旧Git历史保持，仍不读测试数据、不发布PR。</span>
