import json
import os
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

from rapid_doc.cli.common import do_parse, read_fn
from rapid_doc.utils.enum_class import MakeMode


class GuiApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("RapidDoc 本地设置界面")
        self.root.geometry("980x860")

        self.pdf_paths: list[Path] = []
        self.parse_method_map = {
            "自动判断": "auto",
            "文本提取": "txt",
            "图像识别": "ocr",
        }
        self.make_mode_map = {
            "通用标记": MakeMode.MM_MD,
            "自然语言标记": MakeMode.NLP_MD,
        }
        self._build_ui()

    def _build_ui(self) -> None:
        container = ttk.Frame(self.root)
        container.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        env_frame = ttk.LabelFrame(container, text="环境变量")
        env_frame.pack(fill=tk.X, padx=4, pady=6)
        self.device_var = tk.StringVar(value=os.environ.get("MINERU_DEVICE_MODE", ""))
        self.model_dir_var = tk.StringVar(value=os.environ.get("RAPID_MODELS_DIR", ""))
        self._add_labeled_entry(env_frame, "推理设备", self.device_var, 0)
        self._add_labeled_entry(env_frame, "模型目录", self.model_dir_var, 1)

        file_frame = ttk.LabelFrame(container, text="文件与输出")
        file_frame.pack(fill=tk.BOTH, expand=False, padx=4, pady=6)
        self.file_list = tk.Listbox(file_frame, height=6)
        self.file_list.grid(row=0, column=0, rowspan=3, sticky="nsew", padx=6, pady=6)
        file_frame.columnconfigure(0, weight=1)

        add_button = ttk.Button(file_frame, text="添加文件", command=self._add_files)
        add_button.grid(row=0, column=1, sticky="ew", padx=6, pady=3)
        remove_button = ttk.Button(file_frame, text="移除选中", command=self._remove_selected)
        remove_button.grid(row=1, column=1, sticky="ew", padx=6, pady=3)

        self.output_dir_var = tk.StringVar()
        self._add_labeled_entry(file_frame, "输出目录", self.output_dir_var, 2, column=1)
        choose_output = ttk.Button(file_frame, text="选择目录", command=self._choose_output_dir)
        choose_output.grid(row=2, column=2, sticky="ew", padx=6, pady=3)

        parse_frame = ttk.LabelFrame(container, text="解析设置")
        parse_frame.pack(fill=tk.X, padx=4, pady=6)
        self.parse_method_var = tk.StringVar(value="自动判断")
        ttk.Label(parse_frame, text="解析方式").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        ttk.OptionMenu(
            parse_frame,
            self.parse_method_var,
            "自动判断",
            *self.parse_method_map.keys(),
        ).grid(row=0, column=1, sticky="w", padx=6, pady=4)
        self.lang_var = tk.StringVar(value="ch")
        self._add_labeled_entry(parse_frame, "语言列表", self.lang_var, 1)
        self.start_page_var = tk.StringVar(value="0")
        self.end_page_var = tk.StringVar(value="")
        self._add_labeled_entry(parse_frame, "起始页", self.start_page_var, 2)
        self._add_labeled_entry(parse_frame, "结束页", self.end_page_var, 3)

        switch_frame = ttk.LabelFrame(container, text="功能开关")
        switch_frame.pack(fill=tk.X, padx=4, pady=6)
        self.formula_enable_var = tk.BooleanVar(value=True)
        self.table_enable_var = tk.BooleanVar(value=True)
        self.checkbox_enable_var = tk.BooleanVar(value=False)
        self._add_checkbutton(switch_frame, "启用公式识别", self.formula_enable_var, 0)
        self._add_checkbutton(switch_frame, "启用表格识别", self.table_enable_var, 1)
        self._add_checkbutton(switch_frame, "启用复选框识别", self.checkbox_enable_var, 2)

        output_frame = ttk.LabelFrame(container, text="输出设置")
        output_frame.pack(fill=tk.X, padx=4, pady=6)
        self.draw_layout_var = tk.BooleanVar(value=True)
        self.draw_span_var = tk.BooleanVar(value=True)
        self.dump_md_var = tk.BooleanVar(value=True)
        self.dump_middle_var = tk.BooleanVar(value=True)
        self.dump_model_var = tk.BooleanVar(value=True)
        self.dump_pdf_var = tk.BooleanVar(value=True)
        self.dump_content_var = tk.BooleanVar(value=True)
        self._add_checkbutton(output_frame, "绘制版面框", self.draw_layout_var, 0)
        self._add_checkbutton(output_frame, "绘制文本框", self.draw_span_var, 1)
        self._add_checkbutton(output_frame, "输出标记文件", self.dump_md_var, 2)
        self._add_checkbutton(output_frame, "输出中间数据文件", self.dump_middle_var, 3)
        self._add_checkbutton(output_frame, "输出模型数据文件", self.dump_model_var, 4)
        self._add_checkbutton(output_frame, "输出原始文档", self.dump_pdf_var, 5)
        self._add_checkbutton(output_frame, "输出内容列表", self.dump_content_var, 6)
        self.make_mode_var = tk.StringVar(value="通用标记")
        ttk.Label(output_frame, text="标记模式").grid(row=3, column=0, sticky="w", padx=6, pady=4)
        ttk.OptionMenu(
            output_frame,
            self.make_mode_var,
            "通用标记",
            *self.make_mode_map.keys(),
        ).grid(row=3, column=1, sticky="w", padx=6, pady=4)

        config_frame = ttk.LabelFrame(container, text="高级配置（结构化文本）")
        config_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=6)
        self.layout_text = self._add_text_panel(config_frame, "版面配置", 0, 0)
        self.ocr_text = self._add_text_panel(config_frame, "文字识别配置", 0, 1)
        self.formula_text = self._add_text_panel(config_frame, "公式配置", 1, 0)
        self.table_text = self._add_text_panel(config_frame, "表格配置", 1, 1)
        self.image_text = self._add_text_panel(config_frame, "图片配置", 2, 0)
        self.checkbox_text = self._add_text_panel(config_frame, "复选框配置", 2, 1)

        action_frame = ttk.Frame(container)
        action_frame.pack(fill=tk.X, padx=4, pady=6)
        ttk.Button(action_frame, text="加载配置", command=self._load_config).pack(side=tk.LEFT, padx=6)
        ttk.Button(action_frame, text="保存配置", command=self._save_config).pack(side=tk.LEFT, padx=6)
        ttk.Button(action_frame, text="开始解析", command=self._run).pack(side=tk.RIGHT, padx=6)

    def _add_labeled_entry(self, parent: ttk.Frame, label: str, var: tk.StringVar, row: int, column: int = 0) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=column, sticky="w", padx=6, pady=4)
        entry = ttk.Entry(parent, textvariable=var, width=40)
        entry.grid(row=row, column=column + 1, sticky="w", padx=6, pady=4)

    def _add_checkbutton(self, parent: ttk.Frame, label: str, var: tk.BooleanVar, index: int) -> None:
        ttk.Checkbutton(parent, text=label, variable=var).grid(
            row=index // 3, column=index % 3, sticky="w", padx=6, pady=4
        )

    def _add_text_panel(self, parent: ttk.Frame, title: str, row: int, column: int) -> ScrolledText:
        frame = ttk.LabelFrame(parent, text=title)
        frame.grid(row=row, column=column, sticky="nsew", padx=6, pady=6)
        parent.columnconfigure(column, weight=1)
        parent.rowconfigure(row, weight=1)
        text = ScrolledText(frame, height=8)
        text.pack(fill=tk.BOTH, expand=True)
        text.insert(tk.END, "{}")
        return text

    def _add_files(self) -> None:
        paths = filedialog.askopenfilenames(
            title="选择文件",
            filetypes=[("文档文件", "*.pdf *.png *.jpeg *.jpg *.bmp *.tiff *.webp")],
        )
        if not paths:
            return
        for path in paths:
            path_obj = Path(path)
            if path_obj not in self.pdf_paths:
                self.pdf_paths.append(path_obj)
                self.file_list.insert(tk.END, str(path_obj))

    def _remove_selected(self) -> None:
        indices = list(self.file_list.curselection())
        if not indices:
            return
        for index in reversed(indices):
            self.file_list.delete(index)
            del self.pdf_paths[index]

    def _choose_output_dir(self) -> None:
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            self.output_dir_var.set(directory)

    def _load_config(self) -> None:
        path = filedialog.askopenfilename(title="加载配置", filetypes=[("配置文件", "*.json")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
        except Exception as exc:
            messagebox.showerror("加载失败", f"配置读取失败：{exc}")
            return
        self._apply_config(data)

    def _save_config(self) -> None:
        path = filedialog.asksaveasfilename(
            title="保存配置",
            defaultextension=".json",
            filetypes=[("配置文件", "*.json")],
        )
        if not path:
            return
        data = self._collect_config()
        try:
            with open(path, "w", encoding="utf-8") as handle:
                json.dump(data, handle, ensure_ascii=False, indent=4)
        except Exception as exc:
            messagebox.showerror("保存失败", f"配置保存失败：{exc}")

    def _collect_config(self) -> dict:
        return {
            "环境变量": {
                "推理设备": self.device_var.get().strip(),
                "模型目录": self.model_dir_var.get().strip(),
            },
            "解析": {
                "解析方式": self.parse_method_var.get().strip(),
                "语言列表": self.lang_var.get().strip(),
                "起始页": self.start_page_var.get().strip(),
                "结束页": self.end_page_var.get().strip(),
                "启用公式识别": self.formula_enable_var.get(),
                "启用表格识别": self.table_enable_var.get(),
                "启用复选框识别": self.checkbox_enable_var.get(),
            },
            "输出": {
                "输出目录": self.output_dir_var.get().strip(),
                "绘制版面框": self.draw_layout_var.get(),
                "绘制文本框": self.draw_span_var.get(),
                "输出标记文件": self.dump_md_var.get(),
                "输出中间数据文件": self.dump_middle_var.get(),
                "输出模型数据文件": self.dump_model_var.get(),
                "输出原始文档": self.dump_pdf_var.get(),
                "输出内容列表": self.dump_content_var.get(),
                "标记模式": self.make_mode_var.get(),
            },
            "配置": {
                "版面配置": self._read_json(self.layout_text),
                "文字识别配置": self._read_json(self.ocr_text),
                "公式配置": self._read_json(self.formula_text),
                "表格配置": self._read_json(self.table_text),
                "图片配置": self._read_json(self.image_text),
                "复选框配置": self._read_json(self.checkbox_text),
            },
        }

    def _apply_config(self, data: dict) -> None:
        env = data.get("环境变量", {})
        parse = data.get("解析", {})
        output = data.get("输出", {})
        cfg = data.get("配置", {})

        self.device_var.set(str(env.get("推理设备", env.get("MINERU_DEVICE_MODE", ""))))
        self.model_dir_var.set(str(env.get("模型目录", env.get("RAPID_MODELS_DIR", ""))))
        self.parse_method_var.set(self._map_parse_method(parse.get("解析方式", parse.get("parse_method", "自动判断"))))
        self.lang_var.set(str(parse.get("语言列表", parse.get("lang_list", "ch"))))
        self.start_page_var.set(str(parse.get("起始页", parse.get("start_page_id", "0"))))
        self.end_page_var.set(str(parse.get("结束页", parse.get("end_page_id", ""))))
        self.formula_enable_var.set(bool(parse.get("启用公式识别", parse.get("formula_enable", True))))
        self.table_enable_var.set(bool(parse.get("启用表格识别", parse.get("table_enable", True))))
        self.checkbox_enable_var.set(bool(parse.get("启用复选框识别", parse.get("checkbox_enable", False))))

        self.output_dir_var.set(str(output.get("输出目录", output.get("output_dir", ""))))
        self.draw_layout_var.set(bool(output.get("绘制版面框", output.get("draw_layout_bbox", True))))
        self.draw_span_var.set(bool(output.get("绘制文本框", output.get("draw_span_bbox", True))))
        self.dump_md_var.set(bool(output.get("输出标记文件", output.get("dump_md", True))))
        self.dump_middle_var.set(bool(output.get("输出中间数据文件", output.get("dump_middle_json", True))))
        self.dump_model_var.set(bool(output.get("输出模型数据文件", output.get("dump_model_output", True))))
        self.dump_pdf_var.set(bool(output.get("输出原始文档", output.get("dump_orig_pdf", True))))
        self.dump_content_var.set(bool(output.get("输出内容列表", output.get("dump_content_list", True))))
        self.make_mode_var.set(self._map_make_mode(output.get("标记模式", output.get("make_md_mode", "通用标记"))))

        self._set_json(self.layout_text, cfg.get("版面配置", cfg.get("layout_config", {})))
        self._set_json(self.ocr_text, cfg.get("文字识别配置", cfg.get("ocr_config", {})))
        self._set_json(self.formula_text, cfg.get("公式配置", cfg.get("formula_config", {})))
        self._set_json(self.table_text, cfg.get("表格配置", cfg.get("table_config", {})))
        self._set_json(self.image_text, cfg.get("图片配置", cfg.get("image_config", {})))
        self._set_json(self.checkbox_text, cfg.get("复选框配置", cfg.get("checkbox_config", {})))

    def _read_json(self, widget: ScrolledText) -> dict:
        text = widget.get("1.0", tk.END).strip()
        if not text:
            return {}
        try:
            data = json.loads(text)
        except Exception:
            messagebox.showerror("配置错误", "配置格式不正确，请检查输入。")
            raise
        if not isinstance(data, dict):
            messagebox.showerror("配置错误", "配置内容必须是对象。")
            raise ValueError("配置内容必须是对象")
        return data

    def _set_json(self, widget: ScrolledText, data: dict) -> None:
        widget.delete("1.0", tk.END)
        widget.insert(tk.END, json.dumps(data, ensure_ascii=False, indent=4))

    def _parse_lang_list(self, raw_text: str, total: int) -> list[str]:
        parts = [item.strip() for item in raw_text.split(",") if item.strip()]
        if not parts:
            return ["ch"] * total
        if len(parts) == 1:
            return parts * total
        if len(parts) != total:
            raise ValueError("语言数量需要与文件数量一致，或只填写一个语言。")
        return parts

    def _map_parse_method(self, value: str) -> str:
        if value in self.parse_method_map:
            return value
        reverse_map = {item: key for key, item in self.parse_method_map.items()}
        return reverse_map.get(value, "自动判断")

    def _map_make_mode(self, value: str) -> str:
        if value in self.make_mode_map:
            return value
        reverse_map = {item: key for key, item in self.make_mode_map.items()}
        return reverse_map.get(value, "通用标记")

    def _run(self) -> None:
        if not self.pdf_paths:
            messagebox.showwarning("提示", "请先添加需要解析的文件。")
            return
        output_dir = self.output_dir_var.get().strip()
        if not output_dir:
            messagebox.showwarning("提示", "请先选择输出目录。")
            return

        device_mode = self.device_var.get().strip()
        model_dir = self.model_dir_var.get().strip()
        if device_mode:
            os.environ["MINERU_DEVICE_MODE"] = device_mode
        if model_dir:
            os.environ["RAPID_MODELS_DIR"] = model_dir

        try:
            lang_list = self._parse_lang_list(self.lang_var.get(), len(self.pdf_paths))
        except ValueError as exc:
            messagebox.showerror("配置错误", str(exc))
            return

        try:
            layout_config = self._read_json(self.layout_text)
            ocr_config = self._read_json(self.ocr_text)
            formula_config = self._read_json(self.formula_text)
            table_config = self._read_json(self.table_text)
            image_config = self._read_json(self.image_text)
            checkbox_config = self._read_json(self.checkbox_text)
        except Exception:
            return

        try:
            start_page_id = int(self.start_page_var.get().strip() or 0)
        except ValueError:
            messagebox.showerror("配置错误", "起始页必须是整数。")
            return
        end_page_raw = self.end_page_var.get().strip()
        end_page_id = None
        if end_page_raw:
            try:
                end_page_id = int(end_page_raw)
            except ValueError:
                messagebox.showerror("配置错误", "结束页必须是整数。")
                return

        pdf_names = [path.stem for path in self.pdf_paths]
        pdf_bytes_list = [read_fn(path) for path in self.pdf_paths]

        try:
            do_parse(
                output_dir=output_dir,
                pdf_file_names=pdf_names,
                pdf_bytes_list=pdf_bytes_list,
                p_lang_list=lang_list,
                backend="pipeline",
                parse_method=self.parse_method_map.get(
                    self.parse_method_var.get().strip(),
                    self.parse_method_var.get().strip(),
                ),
                formula_enable=self.formula_enable_var.get(),
                table_enable=self.table_enable_var.get(),
                layout_config=layout_config,
                ocr_config=ocr_config,
                formula_config=formula_config,
                table_config=table_config,
                checkbox_config=checkbox_config,
                image_config=image_config,
                f_draw_layout_bbox=self.draw_layout_var.get(),
                f_draw_span_bbox=self.draw_span_var.get(),
                f_dump_md=self.dump_md_var.get(),
                f_dump_middle_json=self.dump_middle_var.get(),
                f_dump_model_output=self.dump_model_var.get(),
                f_dump_orig_pdf=self.dump_pdf_var.get(),
                f_dump_content_list=self.dump_content_var.get(),
                f_make_md_mode=self.make_mode_map.get(
                    self.make_mode_var.get(),
                    self.make_mode_var.get(),
                ),
                start_page_id=start_page_id,
                end_page_id=end_page_id,
            )
        except Exception as exc:
            messagebox.showerror("执行失败", f"解析失败：{exc}")
            return

        messagebox.showinfo("完成", "解析完成，请查看输出目录。")


if __name__ == "__main__":
    root = tk.Tk()
    app = GuiApp(root)
    root.mainloop()
