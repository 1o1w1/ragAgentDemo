# Python 编程指南

## 简介

Python 是一种高级、解释型、通用编程语言，由 Guido van Rossum 于 1991 年首次发布。Python 的设计哲学强调代码的可读性和简洁性。

## 基础语法

### 变量和数据类型

Python 支持多种内置数据类型：

- **整数 (int)**: 如 `42`, `-10`, `0`
- **浮点数 (float)**: 如 `3.14`, `-0.5`, `1.0`
- **字符串 (str)**: 如 `"Hello"`, `'World'`
- **布尔值 (bool)**: `True` 或 `False`
- **列表 (list)**: 如 `[1, 2, 3]`
- **字典 (dict)**: 如 `{"name": "Alice", "age": 25}`

### 控制流

Python 使用缩进来表示代码块：

```python
if condition:
    print("条件为真")
elif another_condition:
    print("另一个条件")
else:
    print("其他情况")
```

### 循环

```python
# for 循环
for i in range(10):
    print(i)

# while 循环
while condition:
    do_something()
```

## 函数

函数使用 `def` 关键字定义：

```python
def greet(name: str) -> str:
    """向用户打招呼"""
    return f"你好, {name}!"
```

### 参数类型

- 位置参数
- 关键字参数
- 默认参数
- 可变参数 `*args` 和 `**kwargs`

## 面向对象编程

```python
class Animal:
    def __init__(self, name: str):
        self.name = name

    def speak(self) -> str:
        raise NotImplementedError

class Dog(Animal):
    def speak(self) -> str:
        return f"{self.name} says Woof!"
```

## 常用标准库

- `os`: 操作系统接口
- `sys`: 系统相关参数
- `json`: JSON 编解码
- `re`: 正则表达式
- `datetime`: 日期时间处理
- `pathlib`: 路径操作
- `typing`: 类型提示

## 虚拟环境

推荐使用虚拟环境管理项目依赖：

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install package_name
```

## 最佳实践

1. 遵循 PEP 8 代码风格指南
2. 使用类型提示提高代码可读性
3. 编写文档字符串
4. 编写单元测试
5. 使用虚拟环境隔离依赖
