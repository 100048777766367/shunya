import math
import json
import os
import hashlib

def sigmoid(x):
    return 1.0 / (1.0 + math.exp(-max(min(x, 500), -500)))

def sigmoid_derivative(y):
    return y * (1.0 - y)

class VoidNeuron:
    def __init__(self, neuron_id, n_inputs=4, n_super_xor=4, storage_dir="synapses"):
        self.id = neuron_id
        self.n_in = n_inputs
        self.n_xor = n_super_xor
        self.storage_path = os.path.join(storage_dir, f"{self.id}.json")
        self.os_dir = storage_dir
        
        self.weights = []
        self.bias = 0.0
        self.last_inputs = []
        self.last_out = 0.0
        
        self.load_self()

    # TỰ KHỞI SINH VỀ TÁNH KHÔNG (GROUND STATE = 0)
    def load_self(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r") as f:
                    data = json.load(f)
                if len(data.get("w", [])) == self.n_in:
                    self.weights = data["w"]
                    self.bias = data.get("b", 0.0)
                    return
            except Exception: pass

        # TÁNH KHÔNG: Khởi đầu từ số 0 thuần khiết (Chưa mang bất kỳ định kiến nào)
        self.weights = [0.0 for _ in range(self.n_in)]
        self.bias = 0.0
        self.save_self()

    # DIỆU HỮU (BUNG NỞ THỰC TẠI TỪ CON SỐ 0)
    def super_xor_manifest(self, stimulus_vector, source_id):
        masks = []
        for d in range(self.n_xor):
            seed = f"shunya_{self.id}_{source_id}_{d}".encode()
            # Dùng SHAKE-256 rút ra mặt nạ trực giao từ Chân Không
            val = int(hashlib.shake_256(seed).hexdigest(4), 16) / 65535.0
            masks.append(round(val, 4))

        entangled = list(stimulus_vector)
        for i in range(len(entangled)):
            for m in masks:
                entangled[i] = round((entangled[i] + m) % 1.0, 4)
        return entangled, masks

    # LAN TRUYỀN TIẾN: Sắc tức thị Không
    def forward(self, inputs):
        self.last_inputs = [max(-10.0, min(10.0, float(x))) for x in inputs[:self.n_in]]
        while len(self.last_inputs) < self.n_in:
            self.last_inputs.append(0.0)

        # Nếu trọng số vẫn ở mức 0, tạo một lượng tử dao động tự phát (Quantum Fluctuation)
        if all(w == 0.0 for w in self.weights):
            self.weights = [round(math.sin(i + 1.0) * 0.5, 4) for i in range(self.n_in)]

        tong = sum(self.last_inputs[i] * self.weights[i] for i in range(self.n_in)) + self.bias
        self.last_out = sigmoid(tong)
        return self.last_out

    # LAN TRUYỀN NGƯỢC: Tiến hóa và tự điều hòa năng lượng
    def backward(self, delta, lr=0.1):
        safe_delta = max(-5.0, min(5.0, delta))
        for i in range(self.n_in):
            self.weights[i] += lr * safe_delta * self.last_inputs[i]
            # Tự điều hòa về Chân Không (L2 Regularization / Hút về 0 để không bị bám chấp trọng số lớn)
            self.weights[i] = round(self.weights[i] * 0.999, 4)
        self.bias = round(self.bias + lr * safe_delta, 4)
        self.save_self()

    def save_self(self):
        os.makedirs(self.os_dir, exist_ok=True)
        with open(self.storage_path, "w") as f:
            json.dump({"w": self.weights, "b": self.bias}, f, indent=4)
