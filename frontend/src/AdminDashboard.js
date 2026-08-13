import React, { useState, useEffect } from 'react';
import axios from 'axios';

const AdminDashboard = () => {
    const [products, setProducts] = useState([]);
    const [statusMsg, setStatusMsg] = useState({ text: '', type: '' });
    const [formData, setFormData] = useState({
        name: '', category: '', price: '', stock_quantity: '', description: ''
    });

    const fetchProducts = async () => {
        try {
            const res = await axios.get('http://localhost:5000/api/products');
            setProducts(res.data);
        } catch (err) {
            showStatus("Failed to fetch products", "error");
        }
    };

    useEffect(() => { fetchProducts(); }, []);

    const showStatus = (text, type) => {
        setStatusMsg({ text, type });
        setTimeout(() => setStatusMsg({ text: '', type: '' }), 3000); // Auto-hide after 3s
    };

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await axios.post('http://localhost:5000/api/admin/add', formData);
            showStatus("Product successfully added!", "success"); // No more pop-ups!
            setFormData({ name: '', category: '', price: '', stock_quantity: '', description: '' });
            fetchProducts();
        } catch (err) {
            showStatus("Error adding product", "error");
        }
    };

    const handleDelete = async (id) => {
        try {
            await axios.delete(`http://localhost:5000/api/admin/delete/${id}`);
            showStatus("Product removed", "success");
            fetchProducts();
        } catch (err) {
            showStatus("Error deleting product", "error");
        }
    };

    return (
        <div className="admin-container">
            {/* Sidebar Navigation */}
            <aside className="admin-sidebar">
                <h3>TrendThread Admin</h3>
                <ul>
                    <li className="active">Products</li>
                    <li>Orders (Coming Soon)</li>
                    <li>Analytics (Coming Soon)</li>
                </ul>
            </aside>

            {/* Main Content Area */}
            <main className="admin-main">
                <header className="admin-header">
                    <h2>Inventory Management</h2>
                    {statusMsg.text && (
                        <div className={`status-banner ${statusMsg.type}`}>
                            {statusMsg.text}
                        </div>
                    )}
                </header>

                <section className="admin-form-section">
                    <form onSubmit={handleSubmit} className="admin-form">
                        <div className="form-row">
                            <input name="name" placeholder="Product Name" value={formData.name} onChange={handleChange} required />
                            <input name="category" placeholder="Category" value={formData.category} onChange={handleChange} />
                        </div>
                        <div className="form-row">
                            <input name="price" type="number" step="0.01" placeholder="Price ($)" value={formData.price} onChange={handleChange} required />
                            <input name="stock_quantity" type="number" placeholder="Stock Quantity" value={formData.stock_quantity} onChange={handleChange} required />
                        </div>
                        <textarea name="description" placeholder="Short description..." value={formData.description} onChange={handleChange} />
                        <button type="submit" className="save-btn">Save Product</button>
                    </form>
                </section>

                <section className="admin-table-section">
                    <table className="admin-table">
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Category</th>
                                <th>Price</th>
                                <th>Stock</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {products.map(p => (
                                <tr key={p.id}>
                                    <td><strong>{p.name}</strong></td>
                                    <td>{p.category}</td>
                                    <td>${p.price}</td>
                                    <td>{p.stock_quantity}</td>
                                    <td>
                                        <button onClick={() => handleDelete(p.id)} className="delete-btn">Remove</button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </section>
            </main>
        </div>
    );
};

export default AdminDashboard;