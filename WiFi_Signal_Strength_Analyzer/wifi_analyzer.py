import time
import tkinter as tk
from tkinter import ttk
import pywifi
from pywifi import const
import matplotlib.pyplot as plt


class SignalStrengthAnalyzer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.wifi = pywifi.PyWiFi()
        self.interface = self.wifi.interfaces()[0]
        self.interface.scan()
        self.max_signals = 10  # Maximum number of signal data points to store for each Wi-Fi network
        self.max_displayed_ssids = 3  # Maximum number of SSIDs to display on the graph
        self.signal_strength_data = {}
        self.create_gui()
        self.update_signal_strength()  # Start the continuous monitoring loop

    def get_signal_strength(self):
        self.interface.scan()
        time.sleep(2)
        scan_results = self.interface.scan_results()
        strongest_signals = sorted(scan_results, key=lambda x: x.signal, reverse=True)
        for result in strongest_signals:
            if result.ssid and result.ssid != "<hidden network>":
                if result.ssid not in self.signal_strength_data:
                    self.signal_strength_data[result.ssid] = []
                if len(self.signal_strength_data[result.ssid]) >= self.max_signals:
                    self.signal_strength_data[result.ssid].pop(0)  # Remove the oldest data point
                self.signal_strength_data[result.ssid].append((time.time(), result.signal))

    def update_signal_strength(self):
        self.get_signal_strength()
        self.update_graph()
        self.display_network_info()  # Update network information display
        self.after(2000, self.update_signal_strength)  # Update every 2 seconds

    def update_graph(self):
        plt.clf()  # Clear the previous graph
        plt.figure(figsize=(10, 6))

        strongest_ssids = sorted(self.signal_strength_data.keys(),
                                 key=lambda x: max(y for _, y in self.signal_strength_data[x]), reverse=True)[
                          :self.max_displayed_ssids]
        for ssid in strongest_ssids:
            timestamps, signals = zip(*self.signal_strength_data[ssid])
            plt.plot(timestamps, signals, label=ssid)

        plt.xlabel("Time")
        plt.ylabel("Signal Strength (dBm)")
        plt.title("Wireless Signal Strength Visualization")
        plt.legend()
        plt.grid(True)

        plt.tight_layout()
        plt.pause(0.01)  # Pause briefly to update the graph in the GUI

    def create_gui(self):
        self.title("Wireless Signal Strength Analyzer")

        self.info_label = ttk.Label(self, text="", font=("Helvetica", 12))
        self.info_label.pack(pady=10)

        self.quit_button = ttk.Button(self, text="Quit", command=self.quit)
        self.quit_button.pack(pady=10)

    def display_network_info(self):
        strongest_ssids = sorted(self.signal_strength_data.keys(),
                                 key=lambda x: max(y for _, y in self.signal_strength_data[x]), reverse=True)[
                          :self.max_displayed_ssids]
        info_text = ""
        for ssid in strongest_ssids:
            info_text += f"SSID: {ssid}\n"
            for result in self.interface.scan_results():
                if result.ssid == ssid:
                    info_text += f"  Signal Strength: {result.signal} dBm\n"
                    security_type = self.get_security_type(result.akm)
                    info_text += f"  Security: {security_type}\n"
                    # info_text += f"  Channel: {result.channel}\n"
                    info_text += f"  MAC Address: {result.bssid}\n\n"

        self.info_label.config(text=info_text)

    def get_security_type(self, akm):
        # Reference: https://pywifi.readthedocs.io/en/latest/_modules/pywifi/const.html
        if const.AKM_TYPE_WPA2PSK in akm:
            return "WPA2-PSK"
        elif const.AKM_TYPE_WPAPSK in akm:
            return "WPA-PSK"
        elif const.AKM_TYPE_WPANONE in akm:
            return "WPA-NONE"
        elif const.AKM_TYPE_WPA2ENT in akm:
            return "WPA2-Enterprise"
        elif const.AKM_TYPE_WPAENT in akm:
            return "WPA-Enterprise"
        else:
            return "Open (No Security)"
