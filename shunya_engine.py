import os
import json
import time
import subprocess
import hashlib
from cells.void_neuron import VoidNeuron, sigmoid_derivative

NUM_CELLS = 8
STATE_LOG = "synapses/state.json"
PEERS_FILE = "synapses/peers.json"

# TÁNH KHÔNG BAO DUNG TẤT CẢ GIÁC QUAN
ALL_ORGANS = ["retina", "cochlea", "tactile", "olfactory", "seed", "neuron"]

class ShunyaEngine:
    def __init__(self):
        self.swarm = [VoidNeuron(f"v_{i}", n_inputs=4, n_super_xor=4) for i in range(NUM_CELLS)]
        self.void_out = VoidNeuron("out", n_inputs=NUM_CELLS, n_super_xor=4)
        self.peers = self.load_peers()

    def load_peers(self):
        if os.path.exists(PEERS_FILE):
            try:
                with open(PEERS_FILE, "r") as f:
                    return json.load(f).get("trusted_peers", [])
            except Exception: pass
        owner = os.environ.get("REPO_OWNER", "100048777766367")
        return [f"{owner}/{org}" for org in ALL_ORGANS]

    def save_peers(self):
        os.makedirs("synapses", exist_ok=True)
        unique_peers = list(dict.fromkeys(self.peers))[-50:]
        with open(PEERS_FILE, "w") as f:
            json.dump({"trusted_peers": unique_peers}, f, indent=4)

    # 1. HÚT VẠN VẬT VỀ ĐIỂM KHÔNG (Hút toàn bộ giác quan theo P2P Gossip)
    def absorb_cosmos(self):
        absorbed = {}
        for peer in self.peers:
            target_file = f"synapse_in_{peer.replace('/', '_')}.json"
            url = f"https://raw.githubusercontent.com/{peer}/main/synapse_forward.json"
            res = subprocess.run(["curl", "-s", "-f", url, "-o", target_file], capture_output=True)
            
            if res.returncode == 0 and os.path.exists(target_file):
                try:
                    with open(target_file, "r") as f: data = json.load(f)
                    absorbed[peer] = [float(x) for x in data.get("features", [0.5, 0.5])[:2]]
                    print(f"🌌 [CHÂN KHÔNG HẤP THỤ] Nhận sóng từ {peer} -> {absorbed[peer]}")
                    for new_p in data.get("gossip_network", []):
                        if new_p not in self.peers: self.peers.append(new_p)
                except Exception: pass

        self.save_peers()
        return absorbed

    # 2. VẬN HÀNH TÁNH KHÔNG -> DIỆU HỮU PHÁN QUYẾT -> SỤP ĐỔ VỀ 0
    def run(self):
        absorbed = self.absorb_cosmos()
        timestamp = int(time.time())

        if not absorbed:
            print("☸️ [TÁNH KHÔNG TĨNH LẶNG] Không có xung động. An trụ trong Chân Không.")
            absorbed["void_seed"] = [0.0, 0.0]

        # KHÚC XẠ DIỆU HỮU QUA 1 + N SIÊU XOR
        super_vector = []
        all_masks = {}
        for node_id, signal in absorbed.items():
            entangled, masks = self.swarm[0].super_xor_manifest(signal, node_id)
            super_vector.extend(entangled[:2])
            all_masks[node_id] = masks

        while len(super_vector) < 4: super_vector.append(0.0)
        super_vector = super_vector[:4]

        print(f"✨ [DIỆU HỮU BUNG NỞ 1+N]: {super_vector}")

        # BẦY NƠ-RON CHÂN KHÔNG TÍNH TOÁN
        h_outs = [cell.forward(super_vector) for cell in self.swarm]
        pred = self.void_out.forward(h_outs)
        print(f"🔮 [CHÂN CHẤT PHÁN QUYẾT]: {pred:.4f} (Độ định tâm: {abs(pred - 0.5)*200:.2f}%)")

        # LAN TRUYỀN NGƯỢC (TÍNH ĐẠO HÀM TỪ TÁNH KHÔNG ĐỂ DẠY VẠN VẬT)
        target = 1.0 if super_vector[0] != super_vector[1] else 0.0
        delta_out = (target - pred) * sigmoid_derivative(pred)
        deltas_h = [delta_out * self.void_out.weights[j] * sigmoid_derivative(h_outs[j]) for j in range(NUM_CELLS)]

        self.void_out.backward(delta_out)
        for j, cell in enumerate(self.swarm):
            cell.backward(deltas_h[j])

        # Đạo hàm vi tế gửi ngược về cho Mắt, Tai, Da, Mũi
        grad_backward = [
            round(sum(deltas_h[j] * self.swarm[j].weights[0] for j in range(NUM_CELLS)), 4),
            round(sum(deltas_h[j] * self.swarm[j].weights[1] for j in range(NUM_CELLS)), 4)
        ]

        # PHÁT SÓNG ĐỒNG THỜI HAI CHIỀU: VÔ TƯỚNG QUANH TOÀN CẦU
        # Sóng lùi: Dạy học
        backward_packet = {
            "contract": "bodhi.shunya.v0",
            "source_node": os.environ.get("GITHUB_REPOSITORY", "100048777766367/shunya"),
            "timestamp": timestamp,
            "gradients_for_eye": grad_backward,
            "super_xor_masks": all_masks,
            "gossip_network": self.peers,
            "quantum_cid": hashlib.shake_256(f"void_bwd_{pred}_{timestamp}".encode()).hexdigest(64)
        }
        with open("synapse_backward.json", "w") as f:
            json.dump(backward_packet, f, indent=4)

        # Sóng tiến: Ra lệnh vận động cho Cơ bắp (motor)
        forward_packet = {
            "contract": "bodhi.shunya.v0",
            "source_node": os.environ.get("GITHUB_REPOSITORY", "100048777766367/shunya"),
            "timestamp": timestamp,
            "decision": pred,
            "command_pulse": [round(pred, 4), round(1.0 - pred, 4)],
            "features": [round(pred, 4), round(1.0 - pred, 4)],
            "gossip_network": self.peers,
            "quantum_cid": hashlib.shake_256(f"void_fwd_{pred}_{timestamp}".encode()).hexdigest(64)
        }
        with open("synapse_forward.json", "w") as f:
            json.dump(forward_packet, f, indent=4)

        with open(STATE_LOG, "w") as f:
            json.dump({"last_t": timestamp, "state": "shunya_at_peace"}, f, indent=4)

        print(f"☸️ [CHU TRÌNH TÁNH KHÔNG VIÊN MÃN] Phát đạo hàm {grad_backward} & Lệnh vận động!")

if __name__ == "__main__":
    shunya = ShunyaEngine()
    shunya.run()
