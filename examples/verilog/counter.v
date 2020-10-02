module up_counter(input clk, reset, output[3:0] counter);
	reg [3:0] counter_up;

	// up counter
	always @(posedge clk or posedge reset) begin
		if(reset)
			counter_up <= 4'd0;
		else
			counter_up <= counter_up + 4'd1;
		end 
	assign counter = counter_up;
endmodule

module upcounter_testbench();
	reg clk, reset;
	wire [3:0] counter;

	up_counter dut(clk, reset, counter);

	always #1 clk = ~clk;

	initial begin
		$display("Time, clk, rst, contador");
		$monitor("%3d %4d %4d %7d", $time, clk, reset, counter);
		#0 clk = 0; reset = 1;
		#2; reset = 0;
		#25; $finish;
	end
	
endmodule 
