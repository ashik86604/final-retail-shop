# RetailHub - Store Management System

A comprehensive, modern **Point of Sale (POS) and Store Management System** built with Python Flask, Supabase, and Bootstrap 5.

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.3+-red.svg)

---

## 📋 Table of Contents

- [Features](#features)
- [Screenshots](#screenshots)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Database Schema](#database-schema)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## ✨ Features

### 🛍️ **Inventory Management**
- Add, edit, and delete products
- Real-time stock tracking
- Low stock alerts
- Inventory value calculation
- Product search and filtering

### 💳 **Smart Billing**
- Create invoices with multiple items
- Automatic GST calculation (18%)
- Customer dropdown selection
- Live bill total calculation
- Multiple payment methods (Cash & Razorpay)

### 👥 **Customer Management**
- Maintain customer database
- Customer contact information
- Purchase history tracking
- Email management for invoices

### 📊 **Analytics & Reports**
- Daily profit breakdown
- Monthly sales trends
- Inventory health analysis
- Customer metrics
- Top performing products
- Sales graphs and charts

### 💰 **Payment Integration**
- **Razorpay Payment Gateway** integration
- Automatic invoice generation and email
- PDF invoice creation
- Email notifications with attachments

### 🤖 **AI Chat Assistant**
- Dynamic query processing
- Today's/Weekly/Monthly sales queries
- Inventory status checks
- Customer information retrieval
- Natural language processing

### 👤 **User Management & Security**
- Role-based access control (Admin/Staff)
- Secure authentication
- Admin-only staff management
- Logout functionality with session clearing
- Route protection

### 📧 **Email & Notifications**
- Invoice delivery via email
- PDF attachments with formatted invoices
- Customer email dropdown selection
- Email notifications on bill creation

### 📱 **Responsive Design**
- Mobile-friendly interface
- Bootstrap 5 styling
- Beautiful gradients and animations
- Dark/Light mode ready

---

## 📸 Screenshots

### Dashboard
![Dashboard](https://via.placeholder.com/800x400?text=Dashboard+Screenshot)
- Total products, customers, and bills
- Today's sales overview
- Inventory value and low stock alerts
- Recent bills and top products

### Inventory Management
![Inventory](https://via.placeholder.com/800x400?text=Inventory+Screenshot)
- Product list with pricing
- Stock status indicators
- Add/Edit/Delete operations
- Real-time search

### Billing System
![Billing](https://via.placeholder.com/800x400?text=Billing+Screenshot)
- Multi-item invoice creation
- Live calculations
- Payment method selection
- Email delivery options

### Admin Panel
![Admin](https://via.placeholder.com/800x400?text=Admin+Panel+Screenshot)
- Staff member management
- Role assignment
- User statistics

### Analytics
![Reports](https://via.placeholder.com/800x400?text=Analytics+Screenshot)
- Sales trends visualization
- Profit analysis
- Inventory metrics
- Customer analytics

---

## 🔧 System Requirements

### Minimum Requirements
- **Python**: 3.8 or higher
- **RAM**: 2GB
- **Storage**: 500MB
- **OS**: Windows, macOS, or Linux

### Required Services
- **Supabase**: PostgreSQL database with authentication
- **Razorpay**: Payment gateway account (optional)
- **Gmail**: For email notifications (optional)

---

## 📦 Installation

### Step 1: Clone Repository
```bash
git clone https://github.com/yourusername/retailhub.git
cd retailhub
