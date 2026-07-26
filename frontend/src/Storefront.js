import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Storefront = () => {
    const [products, setProducts] = useState([]);

    useEffect(() => {
        axios.get('http://localhost:5000/api/products')
            .then(response => setProducts(response.data))
            .catch(error => console.error("Error:", error));
    }, []);

    return (
        <div style={{ padding: '40px' }}>
            <h1>TrendThread Shop</h1>
            <div className="product-list">
                {products.map(p => (
                    <div key={p.id} style={{ border: '1px solid #ddd', padding: '10px', margin: '10px 0' }}>
                        <h3>{p.name}</h3>
                        <p>${p.price}</p>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Storefront;