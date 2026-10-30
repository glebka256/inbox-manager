#!/usr/bin/env python3
"""
Simple GUI test to verify tkinter is working
"""
import tkinter as tk
from tkinter import messagebox

def test_gui():
    print("Creating test window...")
    root = tk.Tk()
    root.title("Test Window | File: utilities/test_gui.py")
    root.geometry("300x200")
    
    label = tk.Label(root, text="GUI Test - This should be visible!", font=("Arial", 12))
    label.pack(pady=20)
    
    def show_message():
        messagebox.showinfo("Test", "GUI is working!")
    
    button = tk.Button(root, text="Click Me!", command=show_message, font=("Arial", 10))
    button.pack(pady=10)
    
    def close_app():
        print("Closing test window...")
        root.destroy()
    
    close_button = tk.Button(root, text="Close", command=close_app, font=("Arial", 10))
    close_button.pack(pady=5)
    
    print("Starting GUI...")
    root.mainloop()
    print("GUI closed.")

if __name__ == "__main__":
    print("Starting GUI test...")
    test_gui()
    print("Test complete.")