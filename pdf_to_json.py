#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF内容提取与结构化工具
读取PDF文件并提取结构化数据，便于存入数据库
"""

import re
import pdfplumber
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class PDFDataExtractor:
    """PDF数据提取器 - 提取结构化数据用于数据库存储"""
    
    def __init__(self, pdf_path: str):
        """
        初始化提取器
        
        Args:
            pdf_path: PDF文件路径
        """
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")
    
    def clean_text(self, text: str) -> str:
        """清理文本中的特殊字符"""
        if not text:
            return ""
        # 移除PDF特殊编码字符
        text = re.sub(r'\(cid:\d+\)', '', text)
        return text.strip()
    
    def extract_header_info(self, text: str) -> Dict[str, Any]:
        """
        提取文档头部信息
        
        Returns:
            包含公司信息、客户信息、单据信息的字典
        """
        data = {
            'company': {},
            'client': {},
            'document': {},
            'process': {}
        }
        
        # 提取公司信息
        company_pattern = r'([A-Z\s&]+LTDA)\s*\n([^\n]+)\s*\nCNPJ/CPF:([\d\./\-]+)'
        company_match = re.search(company_pattern, text)
        if company_match:
            data['company']['name'] = company_match.group(1).strip()
            data['company']['address'] = company_match.group(2).strip()
            data['company']['cnpj'] = company_match.group(3).strip()
        
        # 提取单据号
        doc_no = re.search(r'Demonstrativo de Despesas No\.\s*(\d+)', text)
        if doc_no:
            data['document']['number'] = doc_no.group(1)
        
        # 提取日期
        issue_date = re.search(r'Data de Emiss[^\n]*:(\d{2}/\d{2}/\d{4})', text)
        if issue_date:
            data['document']['issue_date'] = issue_date.group(1)
        
        due_date = re.search(r'Vencimento:\s*(\d{2}/\d{2}/\d{4})', text)
        if due_date:
            data['document']['due_date'] = due_date.group(1)
        
        # 提取客户信息
        client_name = re.search(r'Cliente:\s*([^\n]+)', text)
        if client_name:
            data['client']['name'] = self.clean_text(client_name.group(1))
        
        client_cnpj = re.search(r'CNPJ/CPF:([\d\./\-]+).*?Inscri', text, re.DOTALL)
        if client_cnpj:
            cnpj_text = client_cnpj.group(1).strip()
            # 提取第二个CNPJ（客户的）
            all_cnpjs = re.findall(r'CNPJ/CPF:([\d\./\-]+)', text)
            if len(all_cnpjs) >= 2:
                data['client']['cnpj'] = all_cnpjs[1].strip()
        
        client_address = re.search(r'Endere[^\n]*\s*([^\n]+No\.:[^\n]+)', text)
        if client_address:
            data['client']['address'] = self.clean_text(client_address.group(1))
        
        city_info = re.search(r'Munic[^\n]*\s*([A-Z\s]+)\s+Bairro:([^\s]+)\s+UF:([A-Z]{2})\s+CEP:([\d\-]+)', text)
        if city_info:
            data['client']['city'] = city_info.group(1).strip()
            data['client']['district'] = city_info.group(2).strip()
            data['client']['state'] = city_info.group(3).strip()
            data['client']['cep'] = city_info.group(4).strip()
        
        # 提取流程信息
        process_no = re.search(r'No\. Processo:\s*([^\s]+)', text)
        if process_no:
            data['process']['number'] = process_no.group(1).strip()
        
        exporter = re.search(r'Export/Import:\s*([^\n]+)', text)
        if exporter:
            data['process']['exporter'] = exporter.group(1).strip()
        
        mawb = re.search(r'MAWB / MBL:\s*([^\s]+)', text)
        if mawb:
            data['process']['mawb'] = mawb.group(1).strip()
        
        di_number = re.search(r'DI/DUIMP/DUE:([\d/\-]+)', text)
        if di_number:
            data['process']['di_number'] = di_number.group(1).strip()
        
        invoice_no = re.search(r'No\. Invoice:\s*(\d+)', text)
        if invoice_no:
            data['process']['invoice_number'] = invoice_no.group(1).strip()
        
        # 提取金额信息
        cif_brl = re.search(r'CIF / FOB:\s*R\$\s*([\d\.,]+)', text)
        if cif_brl:
            data['process']['cif_brl'] = cif_brl.group(1).replace('.', '').replace(',', '.')
        
        fob_usd = re.search(r'FOB:\s*USD\s*([\d\.,]+)', text)
        if fob_usd:
            data['process']['fob_usd'] = fob_usd.group(1).replace('.', '').replace(',', '.')
        
        cif_usd = re.search(r'CIF:\s*USD\s*([\d\.,]+)', text)
        if cif_usd:
            data['process']['cif_usd'] = cif_usd.group(1).replace('.', '').replace(',', '.')
        
        exchange_rate = re.search(r'Taxa Dolar:\s*([\d\.,]+)', text)
        if exchange_rate:
            data['process']['exchange_rate_usd'] = exchange_rate.group(1).replace(',', '.')
        
        return data
    
    def extract_expense_items(self, text: str) -> List[Dict[str, Any]]:
        """
        提取费用明细项目
        
        Returns:
            费用项目列表
        """
        items = []
        
        # 匹配费用明细行
        # 格式: 日期 代码 描述 金额(贷方或借方)
        pattern = r'(\d{2}\.\d{2}\.\d{4})\s+(\d+)\s+([A-Z\s\.\%]+?)\s+([\d\.,]+)'
        
        matches = re.finditer(pattern, text)
        
        for match in matches:
            date_str = match.group(1)
            code = match.group(2)
            description = match.group(3).strip()
            amount = match.group(4).replace('.', '').replace(',', '.')
            
            # 判断是贷方还是借方（根据描述中是否有负号或特定关键词）
            is_credit = True  # 默认为贷方
            full_line = text[max(0, match.start()-50):match.end()+50]
            
            # 检查该金额在文本中的上下文
            if any(keyword in description for keyword in ['IRRF', 'CSLL', 'PIS 0', 'COFINS 3']):
                # 这些通常是借方（退款）
                is_credit = False
                
            item = {
                'date': date_str,
                'code': code,
                'description': description,
                'amount': float(amount),
                'type': 'credit' if is_credit else 'debit'
            }
            items.append(item)
        
        return items
    
    def extract_totals(self, text: str) -> Dict[str, float]:
        """提取总计信息"""
        totals = {}
        
        # 提取总计行
        total_pattern = r'TOTAL\s*=>\s*([\d\.,]+)\s+([\d\.,]+)'
        total_match = re.search(total_pattern, text)
        
        if total_match:
            try:
                totals['total_credit'] = float(total_match.group(1).replace('.', '').replace(',', '.'))
                totals['total_debit'] = float(total_match.group(2).replace('.', '').replace(',', '.'))
                totals['balance'] = totals['total_credit'] - totals['total_debit']
            except ValueError:
                pass
        
        # 提取余额说明
        balance_pattern = r'SALDO A FAVOR DE.*?=>\s*([\d\.,]+)'
        balance_match = re.search(balance_pattern, text)
        if balance_match:
            try:
                amount_str = balance_match.group(1).replace('.', '').replace(',', '.')
                if amount_str:  # 确保不是空字符串
                    totals['balance_amount'] = float(amount_str)
            except (ValueError, AttributeError):
                pass
        
        return totals
    
    def extract_all_data(self) -> Dict[str, Any]:
        """
        提取PDF所有结构化数据
        
        Returns:
            完整的结构化数据
        """
        result = {
            'header': {},
            'items': [],
            'totals': {},
            'raw_tables': []
        }
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for page in pdf.pages:
                # 提取文本
                text = page.extract_text()
                
                if text:
                    # 提取头部信息
                    result['header'] = self.extract_header_info(text)
                    
                    # 提取费用项目
                    result['items'] = self.extract_expense_items(text)
                    
                    # 提取总计
                    result['totals'] = self.extract_totals(text)
                
                # 提取表格（作为备用）
                tables = page.extract_tables()
                if tables:
                    result['raw_tables'] = tables
        
        return result
    
    def print_formatted_data(self, data: Dict[str, Any]):
        """
        以格式化的方式打印数据（保持与PDF类似的格式）
        """
        print("\n" + "="*80)
        print("📄 PDF 内容结构化提取结果")
        print("="*80)
        
        # 打印公司信息
        if data['header'].get('company'):
            company = data['header']['company']
            print(f"\n🏢 【公司信息】")
            print(f"   公司名称: {company.get('name', 'N/A')}")
            print(f"   公司地址: {company.get('address', 'N/A')}")
            print(f"   CNPJ: {company.get('cnpj', 'N/A')}")
        
        # 打印单据信息
        if data['header'].get('document'):
            doc = data['header']['document']
            print(f"\n📋 【单据信息】")
            print(f"   单据编号: {doc.get('number', 'N/A')}")
            print(f"   开具日期: {doc.get('issue_date', 'N/A')}")
            print(f"   到期日期: {doc.get('due_date', 'N/A')}")
        
        # 打印客户信息
        if data['header'].get('client'):
            client = data['header']['client']
            print(f"\n👤 【客户信息】")
            print(f"   客户名称: {client.get('name', 'N/A')}")
            print(f"   CNPJ: {client.get('cnpj', 'N/A')}")
            print(f"   地址: {client.get('address', 'N/A')}")
            print(f"   城市: {client.get('city', 'N/A')}")
            print(f"   区域: {client.get('district', 'N/A')}")
            print(f"   州: {client.get('state', 'N/A')}")
            print(f"   邮编: {client.get('cep', 'N/A')}")
        
        # 打印流程信息
        if data['header'].get('process'):
            proc = data['header']['process']
            print(f"\n📦 【流程信息】")
            print(f"   流程编号: {proc.get('number', 'N/A')}")
            print(f"   出口商: {proc.get('exporter', 'N/A')}")
            print(f"   MAWB/MBL: {proc.get('mawb', 'N/A')}")
            print(f"   DI编号: {proc.get('di_number', 'N/A')}")
            print(f"   发票号: {proc.get('invoice_number', 'N/A')}")
            print(f"   CIF (BRL): R$ {proc.get('cif_brl', 'N/A')}")
            print(f"   FOB (USD): $ {proc.get('fob_usd', 'N/A')}")
            print(f"   CIF (USD): $ {proc.get('cif_usd', 'N/A')}")
            print(f"   美元汇率: {proc.get('exchange_rate_usd', 'N/A')}")
        
        # 打印费用明细
        if data['items']:
            print(f"\n💰 【费用明细】")
            print(f"{'日期':<12} {'代码':<8} {'描述':<40} {'金额':>15} {'类型':<8}")
            print("-" * 90)
            
            for item in data['items']:
                type_label = '贷方' if item['type'] == 'credit' else '借方'
                amount_str = f"{item['amount']:,.2f}"
                print(f"{item['date']:<12} {item['code']:<8} {item['description']:<40} {amount_str:>15} {type_label:<8}")
        
        # 打印总计
        if data['totals']:
            totals = data['totals']
            print(f"\n" + "="*90)
            print(f"{'总计贷方:':<60} {totals.get('total_credit', 0):>15,.2f}")
            print(f"{'总计借方:':<60} {totals.get('total_debit', 0):>15,.2f}")
            print("-" * 90)
            print(f"{'余额:':<60} {totals.get('balance_amount', 0):>15,.2f}")
            print("="*90)
        
        print("\n✅ 数据提取完成\n")
    
    def get_database_records(self, data: Dict[str, Any]) -> Dict[str, List[Dict]]:
        """
        将提取的数据转换为数据库记录格式
        
        Returns:
            包含各个表的记录的字典
        """
        records = {
            'documents': [],
            'companies': [],
            'clients': [],
            'processes': [],
            'expense_items': []
        }
        
        # 文档记录
        if data['header'].get('document'):
            doc = data['header']['document']
            records['documents'].append({
                'document_number': doc.get('number'),
                'issue_date': doc.get('issue_date'),
                'due_date': doc.get('due_date'),
                'total_credit': data['totals'].get('total_credit'),
                'total_debit': data['totals'].get('total_debit'),
                'balance': data['totals'].get('balance_amount'),
                'created_at': datetime.now().isoformat()
            })
        
        # 公司记录
        if data['header'].get('company'):
            company = data['header']['company']
            records['companies'].append({
                'name': company.get('name'),
                'address': company.get('address'),
                'cnpj': company.get('cnpj')
            })
        
        # 客户记录
        if data['header'].get('client'):
            client = data['header']['client']
            records['clients'].append({
                'name': client.get('name'),
                'cnpj': client.get('cnpj'),
                'address': client.get('address'),
                'city': client.get('city'),
                'district': client.get('district'),
                'state': client.get('state'),
                'cep': client.get('cep')
            })
        
        # 流程记录
        if data['header'].get('process'):
            proc = data['header']['process']
            records['processes'].append({
                'document_number': data['header'].get('document', {}).get('number'),
                'process_number': proc.get('number'),
                'exporter': proc.get('exporter'),
                'mawb': proc.get('mawb'),
                'di_number': proc.get('di_number'),
                'invoice_number': proc.get('invoice_number'),
                'cif_brl': proc.get('cif_brl'),
                'fob_usd': proc.get('fob_usd'),
                'cif_usd': proc.get('cif_usd'),
                'exchange_rate_usd': proc.get('exchange_rate_usd')
            })
        
        # 费用项目记录
        doc_number = data['header'].get('document', {}).get('number')
        for item in data['items']:
            records['expense_items'].append({
                'document_number': doc_number,
                'expense_date': item['date'],
                'expense_code': item['code'],
                'description': item['description'],
                'amount': item['amount'],
                'transaction_type': item['type']
            })
        
        return records


def main():
    """主函数 - 提取PDF数据并显示"""
    
    pdf_file = "P1.pdf"
    
    try:
        print("\n🚀 开始处理PDF文件...")
        
        # 创建提取器
        extractor = PDFDataExtractor(pdf_file)
        
        # 提取所有数据
        data = extractor.extract_all_data()
        
        # 格式化打印数据
        extractor.print_formatted_data(data)
        
        # 获取数据库记录格式
        db_records = extractor.get_database_records(data)
        
        # 显示数据库记录预览
        print("\n" + "="*80)
        print("💾 【数据库记录格式预览】")
        print("="*80)
        
        for table_name, records in db_records.items():
            if records:
                print(f"\n📊 表名: {table_name}")
                print(f"   记录数: {len(records)}")
                print(f"   示例记录:")
                for key, value in list(records[0].items())[:5]:  # 显示前5个字段
                    print(f"      {key}: {value}")
                if len(records[0]) > 5:
                    print(f"      ... (共 {len(records[0])} 个字段)")
        
        print("\n" + "="*80)
        print("✨ 处理完成！数据已准备好存入数据库")
        print("="*80)
        
        return data, db_records
        
    except FileNotFoundError as e:
        print(f"❌ 错误: {e}")
    except Exception as e:
        print(f"❌ 处理过程中出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

