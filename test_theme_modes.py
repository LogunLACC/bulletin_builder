import customtkinter as ctk
import sys

def test_appearance_modes():
    root = ctk.CTk()
    for mode in ["Light", "Dark", "Hybrid"]:
        try:
            if mode == "Hybrid":
                ctk.set_appearance_mode("Light")
                # Simulate hybrid by setting a panel color
                panel = ctk.CTkFrame(root, fg_color="#222222")
                panel.pack()
                root.update_idletasks()
                panel.destroy()
            else:
                ctk.set_appearance_mode(mode)
                panel = ctk.CTkFrame(root)
                panel.pack()
                root.update_idletasks()
                panel.destroy()
            print(f"[PASS] {mode} mode applied without error.")
        except Exception as e:
            print(f"[FAIL] {mode} mode: {e}")
    root.destroy()

if __name__ == "__main__":
    test_appearance_modes()
