<?php

// A function with no type declarations that returns a sum.
// This will cause type mismatch issues when called with a string.
function add($a, $b) {
    return $a + $b;
}

// Calling add() with an integer and a string should trigger a type error.
echo add(5, 'test');

// Using an undefined variable.
echo $undefinedVar;

// Conditional block that is always false.
// This may be flagged as unreachable code.
if (false) {
    echo "This will never be executed.";
    return;
}

// A class with a missing method.
class Foo {
    private $bar;
    
    // Missing type declaration for $bar parameter.
    public function __construct($bar) {
        $this->bar = $bar;
    }
    
    // This method returns $bar, but there's no guarantee about its type.
    public function getBar() {
        return $this->bar;
    }
}

// Instantiating Foo and then calling a non-existent method 'baz'.
$foo = new Foo(42);
echo $foo->baz();

// Function with unreachable code after a return.
function doSomething() {
    return "Done";
    echo "This code is unreachable.";
}

// A call to a function that does not exist.
nonExistentFunction();
