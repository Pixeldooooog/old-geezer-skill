# 增量合并逻辑

## 任务

用户追加了新素材，需要与现有老登 Skill 合并。

## 处理流程

### 1. 读取现有文件

```
cognition.md  → 当前思维模型
rhetoric.md   → 当前话术画像
style.md      → 当前说话风格
meta.json     → 元数据
features.json → 特征统计数据（如有）
```

### 2. 解析并分析新素材

```bash
python3 tools/source_parser.py "{new_file}" --output /tmp/geezer_new_raw.json
python3 tools/feature_extractor.py --input /tmp/geezer_new_raw.json --target-speaker "{target}" --output /tmp/geezer_new_features.json
```

按 `geezer_analyzer.md` 的维度分析新素材，输出增量内容。

### 3. 增量分类

将新内容分为三类：

| 类型 | 处理方式 |
|------|----------|
| **新发现** | 追加到对应维度（如发现了新的口头禅、新的说教触发点） |
| **增强** | 加强现有维度的权重或细节（如打断频率从"偶尔"升级为"经常"） |
| **矛盾** | 标记冲突，默认以新素材为准，保留旧记录供回滚 |

### 4. 合并规则

#### 话术层（rhetoric.md）
- **口头禅**：新口头禅追加到列表，如果重复出现则提升优先级
- **打断模式**：新的打断方式追加，频率取更高值（越打断越像老登）
- **说教模式**：新的触发条件追加，新的说教套路追加
- **不懂装懂**：新的回避策略追加

#### 认知层（cognition.md）
- **世界观**：新素材中反复出现的主题可能揭示新的核心信念，追加并标注来源
- **决策逻辑**：如果新素材显示了不同的推理模式，记录并存档旧模式
- **价值层级**：新素材可能调整价值排序，更新并保留旧排序作为备注
- **认知偏见**：新证据可能强化或挑战已有偏见识别
- **信息过滤**：新素材可能扩大关注/忽略的范围

#### 风格层（style.md）
- **语气词**：高频词合并去重
- **情绪模式**：新素材中的情绪表现覆盖旧描述（因为更近的素材更准确）

#### 权重（meta.json）
- 重新运行 `feature_extractor.py` 对合并后的全部语料，重新计算 `auto_weights`
- `manual_weights` 保留不变（用户手动调整过的）
- 如果 auto_weights 与 manual_weights 有显著差异，提示用户确认

### 5. 输出

- 修改后的 `cognition.md`
- 修改后的 `rhetoric.md`
- 修改后的 `style.md`
- 更新 `meta.json` 的 `updated_at`、`version`（v1 → v2）、`sources` 列表、`auto_weights`
- 更新 `features.json`
- 重新生成 `SKILL.md`

### 6. 合并后验证

```bash
python3 tools/validator.py --features features.json --skill SKILL.md --output /tmp/merge_validation.json
```

如果有显著矛盾（fidelity_score < 70 的维度），提示用户确认。
用合并后的 Skill 生成一段示例输出，让用户确认是否比之前更像。
