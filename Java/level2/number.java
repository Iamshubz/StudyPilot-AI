package level2;
import java.util.*;
public class number {
    public static void main(String[]args){
        int number;
        Scanner sc = new Scanner(System.in);
        System.out.print("enter you number:");
        number= sc.nextInt();
       if (number%2==0){
            System.out.println("number is even");
       }
       else{
        System.out.println("the number is odd");       }
     sc.close();
    }
}
