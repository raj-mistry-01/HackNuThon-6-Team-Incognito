import bcrypt from 'bcryptjs';
import User from '../Models/User.model.js'

const signupUser = async (req, res) => {
    try {
        console.log("Signup called");
        
        const { fullname, email, password } = req.body;

        if (!fullname) return res.status(400).json({ error: "Full name is required" });
        if (!email) return res.status(400).json({ error: "Email is required" });
        if (!password) return res.status(400).json({ error: "Password is required" });

        // Check if user already exists
        const existingUser = await User.findOne({ email });
        if (existingUser) {
            return res.status(400).json({ error: "Email already in use" });
        }

        const hashedPassword = await bcrypt.hash(password, 10);

        const newUser = new User({
            fullName: fullname,
            email,
            password: hashedPassword
        });

        await newUser.save();

        res.status(201).json({ message: "User registered successfully" });

    } catch (error) {
        console.error("Signup error:", error);
        res.status(500).json({ error: "Internal Server Error" });
    }
};

export {signupUser};
