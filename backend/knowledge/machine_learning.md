# 机器学习基础

## 概述

机器学习 (Machine Learning) 是人工智能的一个分支，它使计算机系统能够从数据中学习和改进，而无需显式编程。

## 机器学习类型

### 监督学习 (Supervised Learning)

监督学习使用标记的训练数据来学习输入和输出之间的映射关系。

**常见算法：**
- 线性回归 (Linear Regression)
- 逻辑回归 (Logistic Regression)
- 决策树 (Decision Trees)
- 随机森林 (Random Forest)
- 支持向量机 (SVM)
- 神经网络 (Neural Networks)

### 无监督学习 (Unsupervised Learning)

无监督学习处理没有标签的数据，寻找数据中的模式和结构。

**常见算法：**
- K-均值聚类 (K-Means Clustering)
- 层次聚类 (Hierarchical Clustering)
- 主成分分析 (PCA)
- 自编码器 (Autoencoders)

### 强化学习 (Reinforcement Learning)

强化学习通过与环境交互来学习最优策略。

**核心概念：**
- 智能体 (Agent)
- 环境 (Environment)
- 状态 (State)
- 动作 (Action)
- 奖励 (Reward)

## 模型评估

### 分类指标

- **准确率 (Accuracy)**: 正确预测的比例
- **精确率 (Precision)**: 预测为正例中真正为正例的比例
- **召回率 (Recall)**: 真正为正例中被预测为正例的比例
- **F1 分数**: 精确率和召回率的调和平均

### 回归指标

- **均方误差 (MSE)**: 预测值与真实值差的平方的平均
- **均方根误差 (RMSE)**: MSE 的平方根
- **平均绝对误差 (MAE)**: 预测值与真实值差的绝对值的平均
- **R² 分数**: 决定系数

## 特征工程

### 特征缩放

- **标准化 (Standardization)**: 将特征缩放到均值为 0，标准差为 1
- **归一化 (Normalization)**: 将特征缩放到 [0, 1] 范围

### 特征选择

- 过滤法 (Filter Methods)
- 包装法 (Wrapper Methods)
- 嵌入法 (Embedded Methods)

## 深度学习

深度学习是机器学习的一个子集，使用多层神经网络来学习数据表示。

### 常见架构

- **卷积神经网络 (CNN)**: 用于图像处理
- **循环神经网络 (RNN)**: 用于序列数据
- **Transformer**: 用于自然语言处理
- **生成对抗网络 (GAN)**: 用于生成模型

### 常用框架

- TensorFlow
- PyTorch
- Keras
- Scikit-learn

## 实践建议

1. 数据质量比数据数量更重要
2. 从简单模型开始，逐步增加复杂度
3. 使用交叉验证评估模型
4. 注意过拟合和欠拟合问题
5. 保持对模型的可解释性关注
