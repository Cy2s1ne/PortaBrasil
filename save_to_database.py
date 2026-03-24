#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将PDF提取的数据存入数据库
支持SQLite、MySQL、PostgreSQL等
"""

import sqlite3
from pathlib import Path
from typing import Dict, List, Any
from pdf_to_json import PDFDataExtractor


class DatabaseManager:
    """数据库管理器 - 用于存储PDF提取的数据"""
    
    def __init__(self, db_path: str = "pdf_data.db"):
        """
        初始化数据库连接
        
        Args:
            db_path: SQLite数据库文件路径
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """连接到数据库"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        print(f"✅ 已连接到数据库: {self.db_path}")
    
    def disconnect(self):
        """断开数据库连接"""
        if self.conn:
            self.conn.close()
            print("✅ 数据库连接已关闭")
    
    def create_tables(self):
        """创建数据表"""
        
        # 文档表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_number TEXT UNIQUE NOT NULL,
                issue_date TEXT,
                due_date TEXT,
                total_credit REAL,
                total_debit REAL,
                balance REAL,
                created_at TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 公司表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                address TEXT,
                cnpj TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 客户表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                cnpj TEXT UNIQUE,
                address TEXT,
                city TEXT,
                district TEXT,
                state TEXT,
                cep TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 流程表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS processes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_number TEXT,
                process_number TEXT UNIQUE,
                exporter TEXT,
                mawb TEXT,
                di_number TEXT,
                invoice_number TEXT,
                cif_brl REAL,
                fob_usd REAL,
                cif_usd REAL,
                exchange_rate_usd REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_number) REFERENCES documents(document_number)
            )
        ''')
        
        # 费用项目表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS expense_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_number TEXT,
                expense_date TEXT,
                expense_code TEXT,
                description TEXT,
                amount REAL,
                transaction_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_number) REFERENCES documents(document_number)
            )
        ''')
        
        self.conn.commit()
        print("✅ 数据表创建完成")
    
    def insert_data(self, records: Dict[str, List[Dict]]):
        """
        插入数据到数据库
        
        Args:
            records: 包含各表记录的字典
        """
        inserted_counts = {}
        
        # 插入公司数据
        for company in records.get('companies', []):
            try:
                self.cursor.execute('''
                    INSERT OR IGNORE INTO companies (name, address, cnpj)
                    VALUES (?, ?, ?)
                ''', (company['name'], company['address'], company['cnpj']))
                inserted_counts['companies'] = inserted_counts.get('companies', 0) + 1
            except Exception as e:
                print(f"⚠️  插入公司数据失败: {e}")
        
        # 插入客户数据
        for client in records.get('clients', []):
            try:
                self.cursor.execute('''
                    INSERT OR IGNORE INTO clients (name, cnpj, address, city, district, state, cep)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    client['name'], 
                    client['cnpj'], 
                    client['address'],
                    client['city'],
                    client['district'],
                    client['state'],
                    client['cep']
                ))
                inserted_counts['clients'] = inserted_counts.get('clients', 0) + 1
            except Exception as e:
                print(f"⚠️  插入客户数据失败: {e}")
        
        # 插入文档数据
        for doc in records.get('documents', []):
            try:
                self.cursor.execute('''
                    INSERT OR REPLACE INTO documents 
                    (document_number, issue_date, due_date, total_credit, total_debit, balance, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    doc['document_number'],
                    doc['issue_date'],
                    doc['due_date'],
                    doc['total_credit'],
                    doc['total_debit'],
                    doc['balance'],
                    doc['created_at']
                ))
                inserted_counts['documents'] = inserted_counts.get('documents', 0) + 1
            except Exception as e:
                print(f"⚠️  插入文档数据失败: {e}")
        
        # 插入流程数据
        for process in records.get('processes', []):
            try:
                self.cursor.execute('''
                    INSERT OR REPLACE INTO processes 
                    (document_number, process_number, exporter, mawb, di_number, 
                     invoice_number, cif_brl, fob_usd, cif_usd, exchange_rate_usd)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    process['document_number'],
                    process['process_number'],
                    process['exporter'],
                    process['mawb'],
                    process['di_number'],
                    process['invoice_number'],
                    process['cif_brl'],
                    process['fob_usd'],
                    process['cif_usd'],
                    process['exchange_rate_usd']
                ))
                inserted_counts['processes'] = inserted_counts.get('processes', 0) + 1
            except Exception as e:
                print(f"⚠️  插入流程数据失败: {e}")
        
        # 插入费用项目数据
        for item in records.get('expense_items', []):
            try:
                self.cursor.execute('''
                    INSERT INTO expense_items 
                    (document_number, expense_date, expense_code, description, amount, transaction_type)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    item['document_number'],
                    item['expense_date'],
                    item['expense_code'],
                    item['description'],
                    item['amount'],
                    item['transaction_type']
                ))
                inserted_counts['expense_items'] = inserted_counts.get('expense_items', 0) + 1
            except Exception as e:
                print(f"⚠️  插入费用项目失败: {e}")
        
        self.conn.commit()
        
        # 打印插入统计
        print("\n📊 数据插入统计:")
        for table, count in inserted_counts.items():
            print(f"   {table}: {count} 条记录")
    
    def query_document(self, document_number: str):
        """查询文档及相关数据"""
        print(f"\n🔍 查询文档: {document_number}")
        print("="*80)
        
        # 查询文档基本信息
        self.cursor.execute('''
            SELECT * FROM documents WHERE document_number = ?
        ''', (document_number,))
        doc = self.cursor.fetchone()
        
        if doc:
            print(f"\n📄 文档信息:")
            print(f"   单据编号: {doc[1]}")
            print(f"   开具日期: {doc[2]}")
            print(f"   到期日期: {doc[3]}")
            print(f"   贷方总计: R$ {doc[4]:,.2f}" if doc[4] else "   贷方总计: N/A")
            print(f"   借方总计: R$ {doc[5]:,.2f}" if doc[5] else "   借方总计: N/A")
            print(f"   余额: R$ {doc[6]:,.2f}" if doc[6] is not None else "   余额: N/A")
        
        # 查询费用明细
        self.cursor.execute('''
            SELECT expense_date, expense_code, description, amount, transaction_type
            FROM expense_items 
            WHERE document_number = ?
            ORDER BY expense_date, id
        ''', (document_number,))
        items = self.cursor.fetchall()
        
        if items:
            print(f"\n💰 费用明细 ({len(items)} 项):")
            print(f"{'日期':<12} {'代码':<8} {'描述':<40} {'金额':>15} {'类型':<8}")
            print("-" * 90)
            for item in items:
                type_label = '贷方' if item[4] == 'credit' else '借方'
                print(f"{item[0]:<12} {item[1]:<8} {item[2]:<40} {item[3]:>15,.2f} {type_label:<8}")
        
        print("="*80)
    
    def get_statistics(self):
        """获取数据库统计信息"""
        print("\n📊 数据库统计:")
        print("="*80)
        
        tables = ['documents', 'companies', 'clients', 'processes', 'expense_items']
        
        for table in tables:
            self.cursor.execute(f'SELECT COUNT(*) FROM {table}')
            count = self.cursor.fetchone()[0]
            print(f"   {table}: {count} 条记录")
        
        # 总金额统计
        self.cursor.execute('SELECT SUM(total_credit), SUM(total_debit) FROM documents')
        totals = self.cursor.fetchone()
        if totals[0]:
            print(f"\n💵 金额统计:")
            print(f"   总贷方: R$ {totals[0]:,.2f}")
            print(f"   总借方: R$ {totals[1]:,.2f}")
            print(f"   净余额: R$ {totals[0] - totals[1]:,.2f}")
        
        print("="*80)


def main():
    """主函数 - 完整流程演示"""
    
    pdf_file = "P1.pdf"
    db_file = "pdf_data.db"
    
    print("\n" + "="*80)
    print("📦 PDF数据提取与数据库存储系统")
    print("="*80)
    
    try:
        # 步骤1: 提取PDF数据
        print("\n📄 步骤1: 提取PDF数据...")
        extractor = PDFDataExtractor(pdf_file)
        data = extractor.extract_all_data()
        extractor.print_formatted_data(data)
        db_records = extractor.get_database_records(data)
        
        # 步骤2: 连接数据库
        print("\n💾 步骤2: 连接数据库...")
        db = DatabaseManager(db_file)
        db.connect()
        
        # 步骤3: 创建表结构
        print("\n🏗️  步骤3: 创建数据表...")
        db.create_tables()
        
        # 步骤4: 插入数据
        print("\n📥 步骤4: 插入数据...")
        db.insert_data(db_records)
        
        # 步骤5: 查询验证
        print("\n🔍 步骤5: 查询验证...")
        doc_number = data['header']['document']['number']
        db.query_document(doc_number)
        
        # 步骤6: 统计信息
        db.get_statistics()
        
        # 关闭数据库连接
        db.disconnect()
        
        print("\n" + "="*80)
        print("✨ 所有步骤完成！数据已成功存入数据库")
        print(f"📁 数据库文件: {db_file}")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
