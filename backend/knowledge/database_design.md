# 数据库设计指南

## 数据库基础

数据库是按照数据结构来组织、存储和管理数据的仓库。

## 数据库类型

### 关系型数据库 (RDBMS)

关系型数据库使用表结构存储数据，支持 SQL 查询。

**常见关系型数据库：**
- MySQL
- PostgreSQL
- Oracle
- SQL Server
- SQLite

### NoSQL 数据库

NoSQL 数据库适用于非结构化或半结构化数据。

**类型：**
- **文档数据库**: MongoDB, CouchDB
- **键值数据库**: Redis, DynamoDB
- **列族数据库**: Cassandra, HBase
- **图数据库**: Neo4j, ArangoDB

## 关系型数据库设计

### 范式化

范式化是减少数据冗余的过程：

- **第一范式 (1NF)**: 每个字段都是原子值
- **第二范式 (2NF)**: 满足 1NF，且非主键字段完全依赖于主键
- **第三范式 (3NF)**: 满足 2NF，且非主键字段不传递依赖于主键

### 反范式化

为了提高查询性能，有时会故意引入冗余数据。

### 表设计示例

```sql
-- 用户表
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 订单表
CREATE TABLE orders (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

## 索引设计

索引可以显著提高查询性能，但会增加写入开销。

### 索引类型

- **主键索引**: 自动创建，唯一且非空
- **唯一索引**: 确保列值唯一
- **普通索引**: 加速查询
- **复合索引**: 多列组合索引

### 索引最佳实践

1. 在经常用于查询条件的列上创建索引
2. 在 JOIN 条件的列上创建索引
3. 避免在频繁更新的列上创建过多索引
4. 使用复合索引时注意列的顺序

## 查询优化

### SQL 优化技巧

1. 避免使用 `SELECT *`
2. 使用 EXPLAIN 分析查询计划
3. 避免在 WHERE 子句中对列进行函数操作
4. 使用适当的数据类型
5. 合理使用 JOIN

### 查询示例

```sql
-- 优化前
SELECT * FROM users WHERE YEAR(created_at) = 2023;

-- 优化后
SELECT * FROM users
WHERE created_at >= '2023-01-01'
AND created_at < '2024-01-01';
```

## 事务处理

事务是一组操作，要么全部成功，要么全部失败。

### ACID 特性

- **原子性 (Atomicity)**: 事务是不可分割的工作单位
- **一致性 (Consistency)**: 事务前后数据库状态一致
- **隔离性 (Isolation)**: 并发事务互不干扰
- **持久性 (Durability)**: 事务提交后永久保存

### 事务示例

```sql
START TRANSACTION;

UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;

COMMIT;
```

## 数据库安全

1. 使用强密码
2. 限制数据库访问权限
3. 定期备份数据
4. 加密敏感数据
5. 防止 SQL 注入

## 数据库维护

- 定期优化表
- 清理过期数据
- 监控数据库性能
- 更新统计信息
