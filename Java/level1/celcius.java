package level1;
import java.util.*;
public class celcius {
    public static void main(String[]args){
        Scanner sc = new Scanner(System.in);
        double celcius,farenhiet;
    System.out.print("enter your celcius temp:");
    celcius = sc.nextDouble();
    farenhiet=(celcius*9/5)+32;
    System.out.print("temprature is in farenhiet:"+farenhiet);
    sc.close();

    }
}