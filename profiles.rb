class Profile

  def initialize(name)
    @name = name
    @base = nil
  end

  def description(desc)
    @desc = desc
  end

  def copy(path:)
    from = @base ? @base : @name
    puts "copy from #{from}:#{path} to #{path}"
  end

  def patch(path:, from: nil)
    from = @base if @base
    puts "patch #{from}:#{path} + #{@name}:#{path} -> #{path}"
  end

  def from(name, &block)
    @base = name
    self.instance_eval(&block)
    @base = nil
  end

end

def define(name, &block)
  profile = Profile.new(name)
  profile.instance_eval(&block)
end


define "pc" do |profile|
  description "office pc, with proxy settings"

  puts "Profile: #{self}"

  copy path: "~/.ssh"

  from "home" do
    copy path: "~"
    patch path: "~/.ssh/config"
    patch path: "~/.gitignore"
  end
end
