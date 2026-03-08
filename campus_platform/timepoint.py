import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random


# ==========================================
# 1. 定义深度时间价值转换网络 (DTVC-Net)
# ==========================================
class PricingNet(nn.Module):
    def __init__(self):
        super(PricingNet, self).__init__()
        # 输入层 4 个特征 -> 隐藏层 16
        self.fc1 = nn.Linear(4, 16)
        self.relu1 = nn.ReLU()
        # 隐藏层 16 -> 隐藏层 8
        self.fc2 = nn.Linear(16, 8)
        self.relu2 = nn.ReLU()
        # 输出层 -> 1 个预测积分
        self.fc3 = nn.Linear(8, 1)

    def forward(self, x):
        x = self.relu1(self.fc1(x))
        x = self.relu2(self.fc2(x))
        x = self.fc3(x)
        return x


# ==========================================
# 2. 生成模拟的历史交易数据 (用于训练)
# 假设平台之前积攒了 2000 条成交记录
# ==========================================
def generate_mock_data(num_samples=2000):
    X = []
    y = []
    for _ in range(num_samples):
        # 特征生成
        time_est = random.uniform(0.5, 5.0)  # 耗时：0.5 到 5 小时
        skill = random.choice([0.0, 0.5, 1.0])  # 技能：0跑腿, 0.5一般, 1.0专业
        urgency = random.choice([0.0, 1.0])  # 紧急：0普通, 1紧急
        traffic = random.uniform(0.0, 1.0)  # 平台拥挤度：0空闲, 1拥挤

        # 模拟真实世界中，这些因素是如何影响最终成交积分的（加入一些随机噪声模拟人类行为）
        # 基础分 = 耗时 * 1.0
        # 技能溢价 = 耗时 * 技能 * 1.5
        # 紧急溢价 = 耗时 * 紧急 * 0.5
        # 拥挤溢价 = 繁忙度带来 10%~30% 的价格上涨
        base_price = time_est * 1.0
        skill_premium = time_est * skill * 1.5
        urgency_premium = time_est * urgency * 0.5

        target_price = (base_price + skill_premium + urgency_premium) * (1 + traffic * 0.3)
        # 加入一点点随机波动(噪声)
        target_price += random.uniform(-0.5, 0.5)

        X.append([time_est, skill, urgency, traffic])
        y.append([max(1.0, target_price)])  # 积分最低为1

    return torch.tensor(X, dtype=torch.float32), torch.tensor(y, dtype=torch.float32)


# ==========================================
# 3. 训练神经网络模型
# ==========================================
def train_model():
    print("开始生成历史数据集...")
    X_train, y_train = generate_mock_data(3000)

    model = PricingNet()
    # 使用均方误差损失函数 (MSE)
    criterion = nn.MSELoss()
    # 使用 Adam 优化器，学习率 0.01
    optimizer = optim.Adam(model.parameters(), lr=0.01)

    print("开始训练 DTVC-Net 神经网络...")
    epochs = 500
    for epoch in range(epochs):
        optimizer.zero_grad()
        outputs = model(X_train)
        loss = criterion(outputs, y_train)
        loss.backward()
        optimizer.step()

        if (epoch + 1) % 100 == 0:
            print(f'Epoch [{epoch + 1}/{epochs}], Loss: {loss.item():.4f}')

    # 保存训练好的模型权重
    torch.save(model.state_dict(), 'dtvc_model.pth')
    print("模型训练完成，已保存为 dtvc_model.pth\n")
    return model


# ==========================================
# 4. 推理/预测函数 (供 Flask 后端调用)
# ==========================================
def predict_points(time_est, skill, urgency, traffic):
    # 加载模型
    model = PricingNet()
    try:
        model.load_state_dict(torch.load('dtvc_model.pth'))
    except FileNotFoundError:
        print("未找到模型文件，先进行训练...")
        model = train_model()

    model.eval()  # 切换到评估模式

    # 构造输入张量
    input_features = torch.tensor([[time_est, skill, urgency, traffic]], dtype=torch.float32)

    with torch.no_grad():
        predicted_tensor = model(input_features)

    # 向上取整，确保积分是整数
    predicted_points = int(np.ceil(predicted_tensor.item()))
    return max(1, predicted_points)  # 最少1积分


if __name__ == '__main__':
    # 1. 运行一次训练
    train_model()

    # 2. 测试几个案例
    print("--- 神经网络预测结果测试 ---")

    p1 = predict_points(time_est=1.0, skill=0.0, urgency=0.0, traffic=0.1)
    print(f"案例A (帮取快递: 1小时, 无技能, 不急, 平台空闲) -> AI建议积分: {p1}")

    p2 = predict_points(time_est=2.0, skill=1.0, urgency=1.0, traffic=0.8)
    print(f"案例B (考前高数急救: 2小时, 高技能, 极急, 平台拥挤) -> AI建议积分: {p2}")