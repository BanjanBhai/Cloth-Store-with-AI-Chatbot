import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';

const Storefront = () => {
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Updated to 127.0.0.1
        axios.get('http://127.0.0.1:5000/api/products')
            .then(res => {
                setProducts(res.data);
                setLoading(false);
            })
            .catch(err => {
                console.error("Storefront Error:", err);
                setLoading(false);
            });
    }, []);

    const getImageUrl = (name) => {
        // Fallback logic for images
        if (name.includes("Shirt")) return "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=500";
        if (name.includes("Jeans")) return "https://images.unsplash.com/photo-1542272604-787c3835535d?w=500";
        if (name.includes("Jacket")) return "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=500";
        return "https://via.placeholder.com/300x400?text=Premium+Apparel";
    };

    if (loading) return <div style={{padding: '50px', textAlign: 'center'}}>Loading products...</div>;

    return (
        <div className="store-container">
            <header className="hero">
                <h1>Premium Apparel</h1>
                <p>Discover the finest fabrics and modern silhouettes.</p>
            </header>

            <div className="product-grid">
                {products.length > 0 ? (
                    products.map(p => (
                        <div key={p.id} className="product-card">
                            <img src={getImageUrl(p.name)} alt={p.name} />
                            <div className="product-info">
                                <span className="category-tag">{p.category || 'New Arrival'}</span>
                                <h3>{p.name}</h3>
                                <p className="price">${p.price}</p>
                                <Link to={`/product/${p.id}`} className="details-link">View Details</Link>
                            </div>
                        </div>
                    ))
                ) : (
                    <p style={{gridColumn: '1/-1', textAlign: 'center'}}>No products found in database.</p>
                )}
            </div>
        </div>
    );
};

export default Storefront;