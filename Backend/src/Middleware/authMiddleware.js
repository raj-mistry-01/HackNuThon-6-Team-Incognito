import jwt from 'jsonwebtoken';

const authMiddleware = (req, res, next) => {
    try {
        const token = req.header("Authorization");

        if (!token) {
            return res.status(401).json({ error: "Access denied. No token provided." });
        }

        const verified = jwt.verify(token, process.env.JWT_SECRET);
        req.user = verified; // Attach user info to request object

        next(); // Proceed to the next middleware or route handler
    } catch (error) {
        res.status(401).json({ error: "Invalid or expired token" });
    }
};

export default authMiddleware;
