fn main() {
    // Unnecessary clone
    let x = String::from("hello");
    let y = x.clone(); // Clippy will warn here about the unnecessary clone
    println!("{}", y);

    // Unused variable
    let unused_var = 42; // Clippy will warn about this

    // Possible panic on unwrap
    let result: Result<i32, &str> = Err("error");
    let value = result.unwrap(); // Clippy will warn about this

    // Redundant reference
    let z = &y; // Clippy might suggest removing the reference here
    println!("{}", z);

    // Inefficient `for` loop
    let vec = vec![1, 2, 3, 4];
    for i in vec.iter() {  // Clippy may suggest using a `for` loop by value
        println!("{}", i);
    }

    // Excessive type annotation
    let a: i32 = 5; // Clippy will suggest removing the type annotation since it's obvious

    // Missing documentation
    let un_documented_function = |x: i32| x * 2; // Clippy may warn about missing documentation
}