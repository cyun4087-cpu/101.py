# Python 基础语法：if、while 和 input 用法

## 1. if 语句

### 基本语法
```python
if 条件:
    执行代码
```

### 示例
```python
# 单条件判断
age = 18
if age >= 18:
    print("已成年")

# if-else 结构
score = 85
if score >= 60:
    print("及格")
else:
    print("不及格")

# if-elif-else 多条件判断
score = 85
if score >= 90:
    print("优秀")
elif score >= 80:
    print("良好")
elif score >= 60:
    print("及格")
else:
    print("不及格")
```

### 嵌套 if 语句
```python
age = 20
if age >= 18:
    if age >= 65:
        print("老年人")
    else:
        print("成年人")
else:
    print("未成年人")
```

---

## 2. while 循环

### 基本语法
```python
while 条件:
    循环体代码
```

### 示例
```python
# 基本循环
count = 0
while count < 5:
    print(f"计数: {count}")
    count += 1

# 无限循环（需要 break 退出）
while True:
    user_input = input("输入 'quit' 退出: ")
    if user_input == 'quit':
        break
    print(f"你输入了: {user_input}")

# 使用 continue 跳过本次循环
count = 0
while count < 10:
    count += 1
    if count % 2 == 0:  # 跳过偶数
        continue
    print(count)  # 只打印奇数

# while-else 结构
count = 0
while count < 3:
    print(f"循环中: {count}")
    count += 1
else:
    print("循环正常结束")
```

### 注意事项
- 确保循环条件最终会变为 False，否则会形成无限循环
- 可以使用 `break` 提前退出循环
- 可以使用 `continue` 跳过本次循环，继续下一次循环

---

## 3. input 函数

### 基本语法
```python
变量名 = input("提示信息")
```

### 示例
```python
# 基本用法
name = input("请输入你的姓名: ")
print(f"你好, {name}!")

# 输入数字（需要类型转换）
age = int(input("请输入你的年龄: "))
print(f"你今年 {age} 岁")

# 输入浮点数
height = float(input("请输入你的身高(米): "))
print(f"你的身高是 {height} 米")

# 结合 if 判断
password = input("请输入密码: ")
if password == "123456":
    print("密码正确")
else:
    print("密码错误")

# 结合 while 循环
while True:
    number = input("请输入一个数字 (输入 'q' 退出): ")
    if number == 'q':
        break
    try:
        num = int(number)
        print(f"你输入的数字是: {num}")
    except ValueError:
        print("请输入有效的数字!")
```

### 注意事项
- `input()` 函数返回的是字符串类型
- 如果需要数字，必须使用 `int()` 或 `float()` 进行类型转换
- 类型转换可能抛出异常，建议使用 try-except 处理

---

## 综合示例

```python
# 猜数字游戏
import random

secret_number = random.randint(1, 100)
attempts = 0
max_attempts = 5

print("欢迎来到猜数字游戏！")
print("我已经想好了一个1到100之间的数字。")

while attempts < max_attempts:
    guess_input = input(f"请输入你的猜测 (还剩 {max_attempts - attempts} 次机会): ")
    
    try:
        guess = int(guess_input)
        attempts += 1
        
        if guess == secret_number:
            print(f"恭喜你！猜对了！用了 {attempts} 次。")
            break
        elif guess < secret_number:
            print("太小了，再试试！")
        else:
            print("太大了，再试试！")
            
    except ValueError:
        print("请输入有效的数字！")
        continue

if attempts >= max_attempts:
    print(f"游戏结束！正确答案是 {secret_number}")
```

